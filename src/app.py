import streamlit as st
from sessions.answer_session import AnswerSession
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from loaders.question_loader import load_questions
from session_logger import save_to_json, load_from_json, save_to_sqlite
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt

load_dotenv()

st.set_page_config(page_title="ESG Service Path", layout="wide")
st.title("ESG Service Path | 淨零小幫手")
st.caption("您好，{}，歡迎來到 {} 的 ESG 診斷問卷。讓我們開始您的永續旅程！".format(
    st.session_state.get("user_name", "訪客"),
    st.session_state.get("company_name", "貴公司")
))

# =====================
# 啟動流程
# =====================
if "industry" not in st.session_state:
    st.warning("請先從 welcome.py 進入並填寫基本資訊。")
    st.stop()

if "stage" not in st.session_state:
    st.session_state.stage = "basic"

user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
question_set = load_questions(st.session_state.industry, st.session_state.stage)

if "session" not in st.session_state:
    session = load_from_json(user_id, question_set)
    if session:
        if st.button("🔄 繼續上次答題進度"):
            st.session_state.session = session
            st.rerun()
        else:
            st.warning("偵測到您有未完成的問卷記錄，您可以選擇繼續或重新開始。")
            st.stop()
    else:
        st.session_state.session = AnswerSession(user_id=user_id, question_set=question_set)

session = st.session_state.session
current_q = session.get_current_question()

# =====================
# 側邊欄 UI
# =====================
with st.sidebar:
    st.header("ESG Service Path")
    st.markdown("---")
    st.markdown(f"👤 使用者：{st.session_state.get('user_name', '')}")
    st.markdown(f"🏢 公司：{st.session_state.get('company_name', '')}")
    st.markdown(f"📘 產業：{st.session_state.industry}")
    st.markdown(f"📶 模式：{'初階診斷' if st.session_state.stage == 'basic' else '進階診斷'}")
    use_gpt = st.checkbox("✅ 啟用 GPT 智能診斷建議", value=True)
    st.markdown("---")
    st.markdown("### 🧭 主題進度統計")
    topic_progress = session.get_topic_progress()
    topics = list(topic_progress.keys())
    answered = [v["answered"] for v in topic_progress.values()]
    totals = [v["total"] for v in topic_progress.values()]

    fig, ax = plt.subplots()
    ax.barh(topics, totals, color="#ddd", label="總題數")
    ax.barh(topics, answered, color="#4CAF50", label="已完成")
    ax.set_xlabel("題數")
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)

# =====================
# 問卷流程
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

progress = session.get_progress()
st.progress(progress["percent"] / 100, text=f"目前進度：{progress['answered']} / {progress['total']} 題")

if current_q:
    topic_name = current_q.get("topic", "未分類")
    st.info(f"📌 目前主題：{topic_name}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if current_q:
    q_text = f"**Q{session.current_index + 1}:** {current_q['text']}"
    with st.chat_message("assistant"):
        st.markdown(q_text)

    st.session_state.messages.append({"role": "assistant", "content": q_text})

    if current_q["type"] == "single":
        response = st.radio("請選擇：", current_q["options"])
    else:
        response = st.multiselect("請選擇一或多個項目：", current_q["options"])

    if st.button("提交回覆"):
        result = session.submit_response(response)
