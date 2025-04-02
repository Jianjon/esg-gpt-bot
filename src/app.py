import streamlit as st
from sessions.answer_session import AnswerSession
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from loaders.question_loader import load_questions
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt

load_dotenv()

st.set_page_config(page_title="ESG Service Path", layout="wide")
st.title("ESG Service Path")
st.caption("讓我們為您提供專屬建議，開始您的 ESG 之旅！")

# =====================
# 檔案儲存與自動續答
# =====================
def get_response_path(user_id):
    return f"data/responses/{user_id}.json"

def save_session_to_json(session):
    os.makedirs("data/responses", exist_ok=True)
    with open(get_response_path(session.user_id), "w", encoding="utf-8") as f:
        json.dump(session.get_summary(), f, ensure_ascii=False, indent=2)

def load_session_from_json(user_id, question_set):
    path = get_response_path(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = AnswerSession(user_id=user_id, question_set=question_set, stage=data.get("stage", "basic"))
        session.responses = data.get("responses", [])
        session.current_index = len(session.responses)
        return session
    return None

# =====================
# 啟動流程
# =====================
if "industry" not in st.session_state:
    st.session_state.industry = st.selectbox("請選擇您所屬的產業：", [
        "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
    ])
    st.stop()

if "stage" not in st.session_state:
    st.session_state.stage = "basic"

user_id = "user1"
question_set = load_questions(st.session_state.industry, st.session_state.stage)

if "session" not in st.session_state:
    session = load_session_from_json(user_id, question_set)
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
    st.markdown(f"📘 當前產業：{st.session_state.industry}")
    st.markdown(f"📶 當前模式：{'初階診斷' if st.session_state.stage == 'basic' else '進階診斷'}")
    use_gpt = st.checkbox("✅ 啟用 GPT 智能診斷建議", value=True)
    st.markdown("---")

    # 主題進度條統計圖
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
# 問卷答題主流程
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 頂部進度條
progress = session.get_progress()
st.progress(progress["percent"] / 100, text=f"目前進度：{progress['answered']} / {progress['total']} 題")

# 顯示主題提示
if current_q:
    topic_name = current_q.get("topic", "未分類")
    st.info(f"📌 目前主題：{topic_name}")

# 歷史訊息紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 顯示題目與互動區
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
        save_session_to_json(session)
        if "error" in result:
            st.error(result["error"])
        else:
            user_input = ", ".join(response) if isinstance(response, list) else response
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

# =====================
# 問卷完成結果顯示 + 進階切換
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

    # 自動儲存結果
    save_session_to_json(session)

    # 進入進階模式按鈕
    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 您已完成初階診斷，是否進入進階診斷？")
        if st.button("👉 進入進階模式"):
            st.session_state.stage = "advanced"
            question_set = load_questions(st.session_state.industry, "advanced")
            st.session_state.session = AnswerSession(user_id=user_id, question_set=question_set)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔄 已切換至進階診斷模式，我們將進行更深入的 ESG 問題探索。"
            })
            st.rerun()
