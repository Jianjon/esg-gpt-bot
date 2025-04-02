import streamlit as st
from sessions.answer_session import AnswerSession
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from dotenv import load_dotenv
import os
import json

load_dotenv()  # 讀取 .env 中的 OPENAI_API_KEY

st.set_page_config(page_title="ESG Service Path", layout="wide")
st.title("ESG Service Path")
st.caption("讓我們為您提供專屬建議，開始您的 ESG 之旅！")

# =====================
# 題庫載入函式
# =====================
def load_questions(stage):
    if stage == "basic":
        with open("data/questions/basic_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open("data/questions/advanced_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)

# =====================
# 側邊欄 UI
# =====================
with st.sidebar:
    st.header("ESG Service Path")
    st.markdown("---")
    st.markdown(f"📘 當前模式：{'初階診斷' if st.session_state.get('stage', 'basic') == 'basic' else '進階診斷'}")
    st.markdown("---")
    use_gpt = st.checkbox("✅ 啟用 GPT 智能診斷建議", value=True)
    st.caption("學習進度將於畫面下方顯示")

# =====================
# 初始化 Session 狀態
# =====================
if "stage" not in st.session_state:
    st.session_state.stage = "basic"

if "session" not in st.session_state:
    st.session_state.session = AnswerSession(
        user_id="user1",
        question_set=load_questions(st.session_state.stage)
    )

session = st.session_state.session
current_q = session.get_current_question()

# =====================
# 對話泡泡 UI
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 顯示目前問題
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
        if "error" in result:
            st.error(result["error"])
        else:
            user_input = ", ".join(response) if isinstance(response, list) else response
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

# =====================
# 問卷完成後報告區
# =====================
else:
    with st.chat_message("assistant"):
        st.success("✅ 問卷已完成，以下是診斷結果：")

    summary = session.get_summary(company_baseline=BaselineManager("data/baselines/company_abc.json").get_baseline())
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []), use_gpt=use_gpt)

    with st.chat_message("assistant"):
        st.markdown("### 📄 報告內容")
        st.markdown(f"```\n{report.generate_text_report()}\n```")

        st.markdown("### 💡 題目建議與診斷")
        for fb in feedback_mgr.generate_feedback():
            st.markdown(f"**Q{fb['question_id']} 建議：** {fb['feedback']}")

        st.markdown("### 📌 總體診斷")
        st.markdown(feedback_mgr.generate_overall_feedback())

    # =====================
    # 是否進入進階模式？
    # =====================
    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 您已完成初階診斷，是否進入進階診斷？")
        if st.button("👉 進入進階模式"):
            st.session_state.stage = "advanced"
            st.session_state.session = AnswerSession(
                user_id="user1",
                question_set=load_questions("advanced")
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔄 已切換至進階診斷模式，我們將進行更深入的 ESG 問題探索。"
            })
            st.rerun()
