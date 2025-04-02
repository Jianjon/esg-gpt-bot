import streamlit as st
from sessions.answer_session import AnswerSession
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager

st.set_page_config(page_title="ESG Service Path", layout="wide")
st.title("ESG Service Path")
st.caption("讓我們為您提供專屬建議，開始您的 ESG 之旅！")

# =====================
# 側邊欄：模擬學習進度與模組導航
# =====================
with st.sidebar:
    st.header("ESG Service Path")
    st.markdown("---")
    st.button("排放源辨識與確認")
    st.button("報告需求與後續行動")
    st.button("數據收集方式與能力")
    st.button("邊界設定與組織資訊")
    st.button("內部管理與SOP現況")
    st.markdown("---")
    st.caption("學習進度")

# =====================
# 初始化題庫與 baseline 載入
# =====================
question_set = [
    {
        "id": 1,
        "text": "貴公司目前採取哪種能源策略？",
        "options": ["可再生能源", "傳統能源", "混合能源"],
        "type": "single"
    },
    {
        "id": 2,
        "text": "貴公司在社會責任方面有哪些措施？",
        "options": ["員工福利", "社區參與", "慈善捐贈"],
        "type": "multiple"
    }
]

baseline_path = "data/baselines/company_abc.json"
bm = BaselineManager(baseline_path)
company_baseline = bm.get_baseline()

# =====================
# 啟動答題 Session
# =====================
if "session" not in st.session_state:
    st.session_state.session = AnswerSession(
        user_id="user1",
        question_set=question_set
    )

session = st.session_state.session
current_q = session.get_current_question()

# =====================
# 對話泡泡互動介面
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
# 完成問卷後：報告與診斷建議
# =====================
else:
    with st.chat_message("assistant"):
        st.success("✅ 問卷已完成，以下是診斷結果：")

    summary = session.get_summary(company_baseline=company_baseline)
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []))

    with st.chat_message("assistant"):
        st.markdown("### 📄 報告內容")
        st.markdown(f"```\n{report.generate_text_report()}\n```")

        st.markdown("### 💡 題目建議與診斷")
        for fb in feedback_mgr.generate_feedback():
            st.markdown(f"**Q{fb['question_id']} 建議：** {fb['feedback']}")

        st.markdown("### 📌 總體診斷")
        st.markdown(feedback_mgr.generate_overall_feedback())
