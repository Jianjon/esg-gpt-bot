import streamlit as st
st.set_page_config(page_title="ESG 淨零小幫手", page_icon="🌱", layout="centered")

from src.welcome import show_welcome_page
if "user_name" not in st.session_state or not st.session_state.get("intro_survey_submitted"):
    show_welcome_page()
    st.stop()

# GPT 預讀快取區
if "gpt_prefetch" not in st.session_state:
    st.session_state["gpt_prefetch"] = {}  # key = qid, value = {"prompt": ..., "option_notes": ...}


import _init_app
from pathlib import Path
import pandas as pd
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# --- 樣式與頁首 ---
with open("assets/custom_style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(f"""
    <style>
        div[data-testid="stAppViewContainer"] > .main {{
            padding-top: 64px;
        }}
    </style>
    <div class="topbar">
        <div class="logo">🌱 ESG Service Path</div>
        <div class="user-info">{st.session_state.get("user_name", "未登入").upper()}</div>
    </div>
""", unsafe_allow_html=True)

# --- 模組與工具 ---
from collections import defaultdict
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from src.utils.session_saver import save_to_json, load_from_json, save_to_sqlite
from src.managers.guided_rag import GuidedRAG
from sessions.answer_session import AnswerSession
from src.components.floating_chatbox import render_floating_chatbox
from src.sessions.context_tracker import add_context_entry, generate_following_action
from src.utils.prompt_builder import generate_option_notes
from src.components.intro_fragment import render_intro_fragment
from src.components.question_guide_fragment import render_question_guide
from src.utils.prompt_builder import generate_user_friendly_prompt

from src.managers.profile_manager import get_user_profile
user_profile = get_user_profile()

if not hasattr(st, "fragment"):
    st.error("⚠️ Streamlit 版本過低，請升級至 1.36.0 以上。")
    st.stop()

# --- 常數與設定 ---
MODULE_MAP = {
    "C": "ESG 教學導入（教學前導）",
    "B": "邊界設定與組織資訊",
    "S": "排放源辨識與確認",
    "D": "數據收集方式與能力",
    "M": "內部管理與SOP現況",
    "R": "報告需求與後續行動"
}
INDUSTRY_FILE_MAP = {
    "餐飲業": "Restaurant.csv", "旅宿業": "Hotel.csv", "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv", "物流業": "Logistics.csv", "辦公室服務業": "Offices.csv"
}
TOPIC_ORDER = list(MODULE_MAP.values())
STAGE_MAP = { "basic": "beginner", "advanced": "intermediate" }

# --- 載入題目 ---
def load_questions(industry, stage="basic", skip_common=False):
    filename = INDUSTRY_FILE_MAP.get(industry)
    path = os.path.join("data", filename)
    df = pd.read_csv(path)
    mapped_stage = STAGE_MAP[stage]
    df = df[df["difficulty_level"].isin([mapped_stage] if stage == "basic" else ["beginner", "intermediate"])]

    questions = []
    for _, row in df.iterrows():
        qid = row["question_id"]
        topic = row.get("topic_category", "").strip() or MODULE_MAP.get(qid[0], "未分類")
        options, option_notes = [], {}
        for opt in ["A", "B", "C", "D", "E"]:
            val = row.get(f"option_{opt}")
            if pd.notna(val): options.append(val); option_notes[val] = row.get(f"option_{opt}_note", "")
        questions.append({
            "id": qid,
            "industry": row.get("industry_type", industry),
            "text": row["question_text"] if pd.notna(row.get("question_text")) else "未填題目內容",
            "options": options,
            "option_notes": option_notes,
            "type": row.get("option_type", "single"),
            "topic": topic,
            "difficulty": row.get("difficulty_level", mapped_stage),
            "report_section": row.get("report_section", ""),
            "tags": row.get("answer_tags", "").split("|") if isinstance(row.get("answer_tags"), str) else [],
            "allow_custom_answer": row.get("allow_custom_answer", False),
            "allow_skip": row.get("allow_skip", False),
            "note": row.get("free_answer_note", ""),
            "question_note": row.get("question_note", ""),
            "learning_objective": row.get("learning_objective", ""),
            "report_topic": row.get("report_topic", ""),
            "learning_goal": row.get("learning_goal", ""),
            "follow_up": row.get("follow_up", "")
        })

    if skip_common:
        questions = [q for q in questions if not q["id"].startswith("C0")]

    def question_sort_key(q):
        topic_index = TOPIC_ORDER.index(q["topic"]) if q["topic"] in TOPIC_ORDER else 999
        num_part = int(q["id"][1:]) if q["id"][1:].isdigit() else 999
        return (topic_index, num_part)

    return sorted(questions, key=question_sort_key)

# --- 問卷 Session 初始化 ---
user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
questions = load_questions(st.session_state.industry, stage=st.session_state.stage, skip_common=True)

def prefetch_gpt_content(session, start_index: int = 1, count: int = 3):
    from src.utils.prompt_builder import generate_user_friendly_prompt
    from src.utils.option_notes import generate_option_notes
    from src.managers.profile_manager import get_user_profile

    user_profile = get_user_profile()

    for offset in range(count):
        index = start_index + offset
        if index >= len(session.question_set):
            break

        q = session.question_set[index]
        qid = q["id"]

        # 若尚未快取
        if qid not in st.session_state["gpt_prefetch"]:
            try:
                print(f"⏳ 預讀中：Q{qid}")
                prompt = generate_user_friendly_prompt(q, user_profile)
                notes = generate_option_notes(q, user_profile)
                st.session_state["gpt_prefetch"][qid] = {
                    "prompt": prompt,
                    "option_notes": notes
                }
                print(f"✅ 預讀完成：Q{qid}")
            except Exception as e:
                print(f"⚠️ 預讀失敗：Q{qid} - {e}")


if "session" not in st.session_state:
    session_file = Path("data/sessions") / f"{st.session_state.company_name}_{st.session_state.user_name}.json"
    if session_file.exists() and not st.session_state.get("reset_data", False):
        session = load_from_json(user_id, questions)
        if session:
            if st.button("🔄 繼續上次答題進度"):
                st.session_state.session = session
                st.session_state["_trigger_all_sections"] += 1
    st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)


# --- 初始化控制變數 ---
if "_trigger_all_sections" not in st.session_state:
    st.session_state["_trigger_all_sections"] = 0


# --- 初始變數 ---
session: AnswerSession = st.session_state["session"]
current_q = session.get_current_question()
if not current_q:
    st.success("🎉 您已完成本階段問卷！")
    st.stop()

# --- 問卷顯示區塊（兩段式）---
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)

qid = current_q["id"]
ready_flag = f"q{qid}_ready"
selected_key = f"selected_{qid}"

if ready_flag not in st.session_state:
    st.session_state[ready_flag] = False
if selected_key not in st.session_state:
    st.session_state[selected_key] = []

# ✅ 第三步：當在第一題時，自動預讀後面幾題 GPT 導讀與選項說明
if session.current_index== 0:
    prefetch_gpt_content(session, start_index=1, count=3)

# === 第一段：導論區塊（尚未準備好時顯示）===
if not st.session_state[ready_flag]:
    is_first = session.question_set.index(current_q) == 0

    # ✅ 嘗試從快取讀取導讀語（intro_prompt），若無則即時生成
    cached = st.session_state["gpt_prefetch"].get(qid, {})
    intro_prompt = cached.get("prompt") or generate_user_friendly_prompt(current_q, user_profile)

    # ✅ 將導讀語傳入元件
    render_intro_fragment(current_q=current_q, is_first_question=is_first, intro_prompt=intro_prompt)

    with st.form(f"ready_form_{qid}"):
        if st.form_submit_button("✅ 我準備好了，開始作答"):
            st.session_state[ready_flag] = True
            st.rerun()


# === 第二段：題目引導與作答（準備好後才顯示）===
if st.session_state[ready_flag]:
    render_question_guide(current_q)

    # ✅ 顯示作答選項
    options = current_q["options"]
    notes_key = f"option_notes_{qid}"
    notes = st.session_state.get(notes_key, {opt: "" for opt in options})
    formatted_options = [f"{opt}：{notes.get(opt, '')}" for opt in options]
    selected = st.session_state.get(selected_key, [])

    if current_q["type"] == "single":
        selected_html = st.radio("請選擇：", formatted_options, key=f"radio_{qid}")
        if selected_html:
            selected = [options[formatted_options.index(selected_html)]]
            st.session_state[selected_key] = selected
    else:
        st.markdown("可複選：")
        for i, html in enumerate(formatted_options):
            cb_key = f"checkbox_{qid}_{options[i]}"
            if st.checkbox(html, key=cb_key, value=options[i] in selected):
                if options[i] not in selected:
                    selected.append(options[i])
            elif options[i] in selected:
                selected.remove(options[i])
        st.session_state[selected_key] = selected

    # ✅ 顯示自訂輸入欄
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input("其他補充（可不填）：", key=f"custom_{qid}")
        if custom_input:
            if current_q["type"] == "single":
                selected = [custom_input]
            else:
                selected.append(custom_input)
            st.session_state[selected_key] = selected

    # ✅ 顯示上下題按鈕
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 上一題", key=f"prev_{qid}"):
            session.go_back()
            st.rerun()

    with col2:
        if st.button("➡️ 下一題（提交答案）", key=f"next_{qid}"):
            if not selected:
                st.warning("⚠️ 請先作答再繼續")
            else:
                # ✅ 提交作答並儲存
                session.submit_response(selected)
                add_context_entry(qid, selected, current_q["text"])
                save_to_json(session)

                try:
                    from src.sessions.context_tracker import generate_following_action
                    full_answer = "、".join(selected) if isinstance(selected, list) else selected
                    suggestion = generate_following_action(current_q, full_answer, user_profile)
                except Exception as e:
                    suggestion = f"⚠️ 無法產生建議：{e}"

                # ✅ 儲存建議內容與顯示狀態
                st.session_state["last_suggestion"] = suggestion
                st.session_state["show_suggestion_box"] = True

                session.go_forward()
                st.rerun()

# === 第三段：顯示 GPT 建議區塊（可關閉）===
if st.session_state.get("show_suggestion_box", False) and st.session_state.get("last_suggestion"):
    with st.container():
        col1, col2 = st.columns([12, 1])
        with col1:
            st.markdown(f"""
                <div class="suggestion-box">
                <strong>💡 根據上一題的建議</strong><br>
                <span style="font-size:15px;">{st.session_state["last_suggestion"]}</span>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("❌", key="close_suggestion", help="關閉提示"):
                st.session_state["show_suggestion_box"] = False


# ✅ 初始化聊天刷新控制變數
if "_trigger_chat_refresh" not in st.session_state:
    st.session_state["_trigger_chat_refresh"] = 0

# ✅ 獨立區塊：右下角聊天視窗
with st.container():
    render_floating_chatbox(question_id=current_q["id"])

# --- 題目跳轉邏輯 ---
if st.session_state.get("jump_to"):
    qid = st.session_state["jump_to"]
    index = next((i for i, item in enumerate(session.question_set) if item["id"] == qid), None)
    if index is not None:
        session.jump_to(index)

        # ✅ [第五步] 補快取：若該題尚未預讀，立即補上
        if qid not in st.session_state["gpt_prefetch"]:
            try:
                from src.utils.prompt_builder import generate_user_friendly_prompt
                from src.utils.option_notes import generate_option_notes

                q = session.question_set[index]
                prompt = generate_user_friendly_prompt(q, user_profile)
                notes = generate_option_notes(q, user_profile)

                st.session_state["gpt_prefetch"][qid] = {
                    "prompt": prompt,
                    "option_notes": notes
                }
                print(f"✅ 跳題補快取完成：{qid}")
            except Exception as e:
                print(f"⚠️ 跳題補快取失敗：{qid} - {e}")

    st.session_state["jump_to"] = None


# --- 側邊欄 ---
from src.components.sidebar_fragment import render_sidebar_fragment

# ✅ 確保 sidebar fragment 不跟主畫面一起 rerun
sidebar_container = st.sidebar
with sidebar_container:
    render_sidebar_fragment(session, current_q)


# --- 完成後診斷報告 ---
if session.current_index >= len(session.question_set):
    baseline = BaselineManager("data/baselines/company_abc.json").get_baseline()
    summary = session.get_summary(company_baseline=baseline)
    summary.update({
        "user_name": st.session_state.get("user_name"),
        "company_name": st.session_state.get("company_name")
    })
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []))

    # --- 顯示診斷摘要報告 ---
    st.markdown("## 📄 診斷摘要報告")
    st.markdown(report.generate_text_report())

    st.markdown("## 💡 題目建議")
    for fb in feedback_mgr.generate_feedback():
        st.markdown(f"- **{fb['question_id']} 建議：** {fb['feedback']}")

    st.markdown("## 📌 總體建議")
    st.markdown(feedback_mgr.generate_overall_feedback())

    save_to_json(session)
    save_to_sqlite(session)

    # --- 初階問卷完成後選項 ---
    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 已完成初階問卷")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 立即產出報告"):
                st.toast("✅ 將根據初階問卷產出報告。")

        with col2:
            if st.button("📈 進入進階問卷"):
                # 建立進階問卷內容
                st.session_state.stage = "advanced"
                new_qset = load_questions(st.session_state.industry, "advanced", skip_common=True)

                # 過濾掉初階答過的題目
                answered_ids = {r["question_id"] for r in session.responses}
                new_qset = [q for q in new_qset if q["id"] not in answered_ids]

                # 產生新 session
                st.session_state.session = AnswerSession(user_id=user_id, question_set=new_qset)
                st.rerun()
