import streamlit as st
st.set_page_config(page_title="ESG 淨零小幫手", page_icon="🌱", layout="centered")

from src.welcome import show_welcome_page

if "user_name" not in st.session_state or not st.session_state.get("intro_survey_submitted"):
    show_welcome_page()
    st.stop()

if "intro_survey_submitted" not in st.session_state:
    st.warning("⚠️ 請先完成 ESG 前導問卷（已整合於 Welcome 頁面）")
    st.stop()

# _init_app 總體處理環境設定與 sys.path
import _init_app

# 套用自定義 CSS 樣式
with open("assets/custom_style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 顯示 Topbar
st.markdown("""
    <style>
        div[data-testid="stAppViewContainer"] > .main {{
            padding-top: 64px;
        }}
    </style>
    <div class="topbar">
        <div class="logo">🌱 ESG Service Path</div>
        <div class="user-info">{}</div>
    </div>
""".format(st.session_state.get("user_name", "未登入").upper()), unsafe_allow_html=True)

from collections import defaultdict
from pathlib import Path
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sessions.context_tracker import get_previous_summary
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from src.utils.session_saver import save_to_json, load_from_json, save_to_sqlite
from src.managers.guided_rag import GuidedRAG
from managers.profile_manager import get_user_profile
from utils.prompt_builder import generate_user_friendly_prompt
import streamlit.runtime.runtime as runtime
from src.components.questionnaire_fragment import render_questionnaire
from src.components.chatbox_fragment import render_chatbox
from sessions.answer_session import AnswerSession  # 確保這行有匯入


if not hasattr(st, "fragment"):
    st.error("⚠️ 目前 Streamlit 版本過低，請升級至 1.36.0 以上才能使用 Fragment 功能。")
    st.stop()

user_profile = get_user_profile()



MODULE_MAP = {
    "C": "ESG 教學導入（教學前導）",
    "B": "邊界設定與組織資訊",
    "S": "排放源辨識與確認",
    "D": "數據收集方式與能力",
    "M": "內部管理與SOP現況",
    "R": "報告需求與後續行動"
}

INDUSTRY_FILE_MAP = {
    "餐飲業": "Restaurant.csv",
    "旅宿業": "Hotel.csv",
    "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv",
    "物流業": "Logistics.csv",
    "辦公室服務業": "Offices.csv"
}

STAGE_MAP = {
    "basic": "beginner",
    "advanced": "intermediate"
}

TOPIC_ORDER = [
    "ESG 教學導入（教學前導）",
    "邊界設定與組織資訊",
    "排放源辨識與確認",
    "數據收集方式與能力",
    "內部管理與SOP現況",
    "報告需求與後續行動"
]

def load_questions(industry: str, stage: str = "basic", skip_common: bool = False) -> list:
    filename = INDUSTRY_FILE_MAP.get(industry)
    if not filename:
        raise ValueError(f"找不到產業對應的題庫：{industry}")
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到題庫檔案：{path}")

    df = pd.read_csv(path)
    required_cols = ["question_id", "question_text", "difficulty_level", "option_type", "answer_tags"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"題庫缺少必要欄位：{col}")

    if stage not in STAGE_MAP:
        raise ValueError(f"輸入值錯誤：stage 應為 basic 或 advanced，但收到：{stage}")
    mapped_stage = STAGE_MAP[stage]
    df = df[df["difficulty_level"].isin([mapped_stage] if stage == "basic" else ["beginner", "intermediate"])]

    questions = []
    for _, row in df.iterrows():
        qid = row["question_id"]
        topic = row.get("topic_category", "").strip() or MODULE_MAP.get(qid[0], "未分類")
        options, option_notes = [], {}
        for opt in ["A", "B", "C", "D", "E"]:
            val = row.get(f"option_{opt}")
            if pd.notna(val):
                options.append(val)
                option_notes[val] = row.get(f"option_{opt}_note", "")

        questions.append({
            "id": qid,
            "industry": row.get("industry_type", industry),
            "text": row.get("question_text", "未填題目內容"),
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
        questions = [q for q in questions if not (q["id"].startswith("C0"))]

    def question_sort_key(q):
        topic_index = TOPIC_ORDER.index(q["topic"]) if q["topic"] in TOPIC_ORDER else 999
        qid = q["id"]
        num_part = int(qid[1:]) if qid[1:].isdigit() else 999
        return (topic_index, num_part)

    return sorted(questions, key=question_sort_key)



# 取得 user_id（用於識別與 session 儲存）
user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"

# 載入題庫（根據產業與階段）
current_stage = st.session_state.stage
questions = load_questions(
    industry=st.session_state.industry,
    stage=current_stage,
    skip_common=True
)


# ===== 初始化問卷 Session（要放在主流程前段，不能放太後面） =====
if "session" not in st.session_state:
    session_file = Path("data/sessions") / f"{st.session_state.company_name}_{st.session_state.user_name}.json"
    if session_file.exists():
        if st.session_state.get("reset_data"):
            session_file.unlink()
            st.toast("✅ 已清除原有紀錄，問卷將從頭開始。")
            st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)

            # ➕ 額外產生 GPT 快取（前 5 題）
            from src.utils.prompt_builder import generate_dynamic_question_block
            from src.utils.gpt_tools import call_gpt

            for q in questions[:5]:
                cache_key = f"gpt_question_intro_{q['id']}"
                if cache_key not in st.session_state:
                    prompt = generate_dynamic_question_block(
                        user_profile=st.session_state["user_intro_survey"],
                        current_q=q,
                        user_answer=""
                    )
                    try:
                        gpt_response = call_gpt(prompt)
                        parts = gpt_response.split("【說明】")
                        title = parts[0].replace("【題目】", "").strip()
                        intro = parts[1].strip()
                    except Exception:
                        title = q.get("text", "")
                        intro = q.get("question_note", "")

                    st.session_state[cache_key] = {
                        "title": title,
                        "intro": intro
                    }

        else:
            session = load_from_json(user_id, questions)
            if session:
                if st.button("🔄 繼續上次答題進度"):
                    st.session_state.session = session
                    st.rerun()
                else:
                    st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)
                    st.rerun()
    else:
        st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)



def get_previous_summary(current_qid: str) -> str:
    summaries = st.session_state.get("context_history", [])
    session = st.session_state.get("session")
    if not session:
        return ""
    idx = next((i for i, q in enumerate(session.question_set) if q["id"] == current_qid), None)
    if idx is None or idx == 0:
        return ""
    prev_qid = session.question_set[idx - 1]["id"]
    match = next((s for s in summaries if s["id"] == prev_qid), None)
    return match["summary"] if match else ""

if "context_history" not in st.session_state:
    st.session_state["context_history"] = []

# ===== 初始化設定 =====
if "stage" not in st.session_state:
    st.session_state.stage = "basic"
if "jump_to" not in st.session_state:
    st.session_state["jump_to"] = None

user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
current_stage = st.session_state.stage

questions = load_questions(
    industry=st.session_state.industry,
    stage=current_stage,
    skip_common=True
)

# ===== 啟用 jump_to 跳題 =====
if st.session_state.get("jump_to"):
    qid = st.session_state["jump_to"]
    index = next((i for i, item in enumerate(session.question_set) if item["id"] == qid), None)
    if index is not None:
        session.jump_to(index)
        st.session_state["jump_to"] = None
        st.rerun()



# ✅ 初始化後就可以使用
session: AnswerSession = st.session_state["session"]


current_q: dict = session.get_current_question()
if not current_q:
    st.warning("⚠️ 找不到目前題目，請重新載入問卷流程")
    st.stop()

# ===== 側邊列重構（使用 question_set） =====
with st.sidebar:
    st.title("📋 ESG Service Path | 淨零小幫手")
    st.markdown("---")
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state["user_name"]}")
    st.markdown(f"**階段：** {'初階' if st.session_state["stage"] == 'basic' else '進階'}")
    st.markdown(f"**目前進度：** {session.current_index + 1} / {len(session.question_set)}")
    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    current_topic = current_q.get("topic") if current_q else None
    answered_ids = {r["question_id"] for r in session.responses}

    questions_by_topic = defaultdict(list)
    for q in session.question_set:
        topic = q.get("topic", "未分類")
        questions_by_topic[topic].append(q)

    for topic, q_list in questions_by_topic.items():
        total = len(q_list)
        answered = sum(1 for q in q_list if q["id"] in answered_ids)
        checked = "✅ " if answered == total else ""
        expanded = topic == current_topic

        with st.expander(f"{checked}{topic}", expanded=expanded):
            for idx, q in enumerate(q_list, 1):
                is_done = q["id"] in answered_ids
                label = f"{idx}. {q.get('text', '')[:15]}..."
                if is_done:
                    label += " ✔"

                key = f"jump_to_{q['id']}"
                if st.button(label, key=key):
                    st.session_state["jump_to"] = q["id"]
                    st.rerun()


# 固定主體容器
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)


# 查詢 RAG 補充資料
rag = GuidedRAG(vector_path="data/vector_output/")
# 取得用戶提問（根據你的 current_q 結構）
user_question = current_q.get("learning_goal") or current_q.get("topic", "")

# 使用 RAG 模組回答（使用 ask() 方法）
rag_response, related_chunks = rag.ask(
    user_question=user_question,
    history=[],       # 若還沒開始對話，可先傳空的
    turn=1            # 第一輪對話
)

# 你可以視需要選擇回傳的 rag_response 或相關 chunk
rag_context = rag_response

# === 自動查詢 RAG 補充知識 ===
query_topic = current_q.get("learning_goal") or current_q.get("topic", "")
rag_context = rag.query(query_topic) if query_topic else ""

# 假設你已經從 `context_tracker` 取得上一題摘要（例如 get_previous_summary(current_q['id'])）
previous_summary = get_previous_summary(current_q["id"])  # ✅ 正確

# GPT AI 顧問引導語區塊
st.markdown('<div class="ai-intro-block">', unsafe_allow_html=True)
st.markdown("#### 💬 AI 淨零顧問引導")

trigger = st.session_state.get("_trigger_all_sections", 0)
cache_key = f"friendly_intro_{current_q['id']}_{trigger}"
tone = st.session_state.get("preferred_tone", "gentle")

if cache_key not in st.session_state:
    with st.spinner("🔄 正在產生顧問引導中..."):
        try:
            from src.utils.prompt_builder import generate_user_friendly_prompt
            st.session_state[cache_key] = generate_user_friendly_prompt(
                current_q=current_q,
                user_profile=st.session_state["user_intro_survey"],
                tone=tone
            )
        except Exception as e:
            st.session_state[cache_key] = f"⚠️ 無法產生引導語：{str(e)}"

st.markdown(f"**{st.session_state[cache_key]}**", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ✅ 不論如何都只顯示快取內容，不重跑 GPT


st.markdown("---")
st.markdown('<div class="question-block">', unsafe_allow_html=True)
render_questionnaire()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-interaction-block">', unsafe_allow_html=True)
render_chatbox()
st.markdown('</div>', unsafe_allow_html=True)



# === 如果所有題目都完成，才顯示完成提示 ===
if session.current_index >= len(session.question_set):
    st.success("🎉 您已完成本階段問卷！")

    # 👉 此處之後可加入「診斷報告、進階問卷切換」的功能（下一步處理）
    # ...
 # ✅ 產生診斷摘要報告
    baseline = BaselineManager("data/baselines/company_abc.json").get_baseline()
    summary = session.get_summary(company_baseline=baseline)
    summary["user_name"] = st.session_state.get("user_name")
    summary["company_name"] = st.session_state.get("company_name")
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []))

    st.markdown("## 📄 診斷摘要報告")
    st.markdown(f"""
{report.generate_text_report()}

""")

    # ✅ 題目建議
    st.markdown("## 💡 題目建議與改善方向")
    for fb in feedback_mgr.generate_feedback():
        st.markdown(f"- **{fb['question_id']} 建議：** {fb['feedback']}")

    # ✅ 總體建議
    st.markdown("## 📌 總體建議")
    st.markdown(feedback_mgr.generate_overall_feedback())

    # ✅ 儲存結果
    save_to_json(session)
    save_to_sqlite(session)

    # ✅ 進階問卷切換（限 basic 階段）
    if st.session_state.stage == "basic":   
        st.divider()
        st.subheader("🚀 您已完成初階診斷")

        st.markdown("請選擇下一步：")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 立即產出報告", key="btn_generate_report_only"):
                st.toast("✅ 將根據初階問卷產出報告。")

        with col2:
            if st.button("📈 進入進階問卷", key="btn_continue_advanced"):
                st.session_state.stage = "advanced"

                # 載入 advanced 題目（包含 intermediate）
                new_qset = load_questions(
                    industry=st.session_state.industry,
                    stage="advanced",
                    skip_common=True
                )

                # 移除已完成的初階題
                answered_ids = {r["question_id"] for r in session.responses}
                new_qset = [q for q in new_qset if q["id"] not in answered_ids]

                # 建立新 session 並跳轉
                st.session_state.session = AnswerSession(user_id=user_id, question_set=new_qset)
                st.rerun()
