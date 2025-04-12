import streamlit as st
st.set_page_config(page_title="ESG 淨零小幫手", page_icon="🌱", layout="centered")

from src.welcome import show_welcome_page
if "user_name" not in st.session_state or not st.session_state.get("intro_survey_submitted"):
    show_welcome_page()
    st.stop()

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
from managers.profile_manager import get_user_profile
from sessions.answer_session import AnswerSession
from src.components.floating_chatbox import render_floating_chatbox
from src.utils.prompt_builder import generate_user_friendly_prompt
from src.utils.question_utils import get_previous_summary
from src.components.questionnaire_fragment import render_questionnaire_fragment

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

if "session" not in st.session_state:
    session_file = Path("data/sessions") / f"{st.session_state.company_name}_{st.session_state.user_name}.json"
    if session_file.exists() and not st.session_state.get("reset_data", False):
        session = load_from_json(user_id, questions)
        if session:
            if st.button("🔄 繼續上次答題進度"):
                st.session_state.session = session
                st.rerun()
    st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)

# --- 初始變數 ---
session: AnswerSession = st.session_state["session"]
current_q = session.get_current_question()
if not current_q:
    st.success("🎉 您已完成本階段問卷！")
    st.stop()

# --- 問卷顯示區塊（兩段式）---
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)
render_questionnaire_fragment()
render_floating_chatbox(question_id=current_q["id"])

# --- 題目跳轉邏輯 ---
if st.session_state.get("jump_to"):
    qid = st.session_state["jump_to"]
    index = next((i for i, item in enumerate(session.question_set) if item["id"] == qid), None)
    if index is not None:
        session.jump_to(index)
        st.session_state["jump_to"] = None
        st.rerun()

# --- 側邊欄 ---
with st.sidebar:
    st.title("📋 ESG Service Path")
    st.markdown("---")
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state['user_name']}")
    st.markdown(f"**階段：** {'初階' if st.session_state['stage'] == 'basic' else '進階'}")
    st.markdown(f"**目前進度：** {session.current_index + 1} / {len(session.question_set)}")
    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    current_topic = current_q.get("topic", "")
    answered_ids = {r["question_id"] for r in session.responses}
    topic_groups = defaultdict(list)
    for q in session.question_set:
        topic_groups[q["topic"]].append(q)

    for topic, q_list in topic_groups.items():
        total = len(q_list)
        answered = sum(1 for q in q_list if q["id"] in answered_ids)
        checked = "✅ " if answered == total else ""
        expanded = topic == current_topic
        with st.expander(f"{checked}{topic}", expanded=expanded):
            for i, q in enumerate(q_list):
                label = f"{i+1}. {q['text'][:20]}{' ✔' if q['id'] in answered_ids else ''}"
                if st.button(label, key=f"jump_to_{q['id']}"):
                    st.session_state["jump_to"] = q["id"]
                    st.rerun()

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

    st.markdown("## 📄 診斷摘要報告")
    st.markdown(report.generate_text_report())
    st.markdown("## 💡 題目建議")
    for fb in feedback_mgr.generate_feedback():
        st.markdown(f"- **{fb['question_id']} 建議：** {fb['feedback']}")
    st.markdown("## 📌 總體建議")
    st.markdown(feedback_mgr.generate_overall_feedback())

    save_to_json(session)
    save_to_sqlite(session)

    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 已完成初階問卷")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 立即產出報告"):
                st.toast("✅ 將根據初階問卷產出報告。")
        with col2:
            if st.button("📈 進入進階問卷"):
                st.session_state.stage = "advanced"
                new_qset = load_questions(st.session_state.industry, "advanced", skip_common=True)
                answered_ids = {r["question_id"] for r in session.responses}
                new_qset = [q for q in new_qset if q["id"] not in answered_ids]
                st.session_state.session = AnswerSession(user_id=user_id, question_set=new_qset)
                st.rerun()
