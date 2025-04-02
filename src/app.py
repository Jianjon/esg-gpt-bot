import streamlit as st
from sessions.answer_session import AnswerSession
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from loaders.question_loader import load_questions
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="ESG Service Path", layout="wide")
st.title("ESG Service Path")
st.caption("讓我們為您提供專屬建議，開始您的 ESG 之旅！")

# =====================
# 產業選擇 + 階段模式管理
# =====================
if "industry" not in st.session_state:
    st.session_state.industry = st.selectbox("請選擇您所屬的產業：", [
        "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
    ])
    st.stop()

if "stage" not in st.session_state:
    st.session_state.stage = "basic"

# =====================
# 側邊欄進度 + GPT 開關
# =====================
with st.sidebar:
    st.header("ESG Service Path")
    st.markdown("---")
    st.markdown(f"📘 當前產業：{st.session_state.industry}")
    st.markdown(f"📶 當前模式：{'初階診斷' if st.session_state.stage == 'basic' else '進階診斷'}")
    st.markdown("---")
    use_gpt = st.checkbox("✅ 啟用 GPT 智能診斷建議", value=True)

# =====================
# 啟動 Session
# =====================
if "session" not in st.session_state:
    question_set = load_questions(st.session_state.industry, st.session_state.stage)
    st.session_state.session = AnswerSession(
        user_id="user1",
        question_set=question_set
    )

session = st.session_state.session
current_q = session.get_current_question()

# =====================
# Chat 對話式問答介面
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示進度條（上方）
progress = session.get_progress()
st.progress(progress["percent"] / 100, text=f"目前進度：{progress['answered']} / {progress['total']} 題")

# 顯示目前主題名稱
if current_q:
    topic_name = current_q.get("topic", "未分類")
    st.info(f"📌 目前主題：{topic_name}")

# 顯示歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 顯示目前題目
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
# 完成答題：產出診斷建議 + 轉進階
# =====================
else:
    with st.chat_message("assistant"):
        st.success("✅ 問卷已完成，以下是診斷結果：")

    baseline = BaselineManager("data/baselines/company_abc.json").get_baseline()
    summary = session.get_summary(company_baseline=baseline)
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

    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 您已完成初階診斷，是否進入進階診斷？")
        if st.button("👉 進入進階模式"):
            st.session_state.stage = "advanced"
            question_set = load_questions(st.session_state.industry, "advanced")
            st.session_state.session = AnswerSession(user_id="user1", question_set=question_set)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔄 已切換至進階診斷模式，我們將進行更深入的 ESG 問題探索。"
            })
            st.rerun()
