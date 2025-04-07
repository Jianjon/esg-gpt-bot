import streamlit as st
from src.loaders.question_loader import load_questions
from src.sessions.answer_session import AnswerSession
from src.sessions import context_tracker
from src.generators.report_generator import generate_basic_report
from src.utils.vector_guard import VectorStore
from src.managers.guided_rag import GuidedRAG
from src.managers.gpt_rewrite import rewrite_question_to_conversational
from src.utils.topic_progress import get_topic_progress
from session_logger import save_to_json
import openai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from src.utils.gpt_tools import call_gpt


# 載入自訂樣式
def local_css(file_path):
    with open(file_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/custom_style.css")

# --- Sidebar：ChatGPT 風格的 ESG Service Path ---
st.sidebar.markdown("## ESG Service Path")
st.sidebar.markdown("---")

# 顯示使用者名稱
user_name = st.session_state.get("user_name", "Guest")
st.sidebar.markdown(f"使用者：**{user_name}**")

# 初始化問卷狀態
if 'welcome_submitted' not in st.session_state or not st.session_state['welcome_submitted']:
    st.warning("請先完成產業選擇與公司基本資料填寫。")
    st.stop()

industry = st.session_state['industry']
stage = st.session_state.get('stage', 'basic')

# 初始化 AnswerSession
user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
questions = load_questions(industry, stage)

if 'session' not in st.session_state:
    st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)

session = st.session_state.session

# 顯示主題進度圖
answered_ids = {r["question_id"] for r in session.responses}
fig = get_topic_progress(session.question_set, answered_ids)
st.sidebar.pyplot(fig)

# 顯示目前題目
current_q = session.get_current_question()
if current_q:
    # 使用 GPT 重寫題目為對話風格
    gpt_text = rewrite_question_to_conversational(
        current_q["text"],
        question_type=current_q.get("type", "single"),
        learning_goal=current_q.get("learning_goal", ""),
        use_gpt=True
    )

    # 顯示題目與 GPT 重寫的對話風格題目
    st.markdown(
        f"<div class='fixed-question'>{current_q['text']}</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"<div class='ai-message'>{gpt_text}</div>", unsafe_allow_html=True)

    # === GPT 對話式問答區塊 ===
    st.divider()
    st.markdown("### 🤖 問題機器人（針對本題進行延伸提問）")

    # 初始化 context_tracker 的 chat 記憶
    if "qa_threads" not in st.session_state:
        st.session_state.qa_threads = {}

    from sessions.context_tracker import get_conversation, add_turn
    from src.utils.gpt_tools import call_gpt  # 你原本自定義的 GPT 呼叫函式

    chat_id = current_q["id"]
    history = get_conversation(chat_id)

    # 顯示對話紀錄（上半部）
    for msg in history:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["gpt"])

    # 加上 follow-up 提示（建議提問方向）
    st.markdown("##### 💡 提問建議")
    st.info(current_q.get("follow_up", "目前尚無提示，您可自由發問"))

# 設定每題最多對話輪數
MAX_TURNS = 5
if len(history) >= MAX_TURNS:
    st.warning("您已針對本題進行了多輪提問，建議前往下一題以持續學習 😊")
    if st.button("👉 前往下一題"):
        session.next()
        st.rerun()
    st.stop()



# 下半部輸入區
if prompt := st.chat_input("針對本題還有什麼問題？可詢問 ESG 專家 AI"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 回覆中..."):
            try:
                # 呼叫改良版 call_gpt，傳入完整參數
                gpt_reply = call_gpt(
                    prompt=prompt,
                    question_text=current_q["text"],
                    learning_goal=current_q.get("learning_goal", ""),
                    chat_history=get_conversation(chat_id),
                    industry=st.session_state.get("industry", "")
                )
                st.markdown(gpt_reply)
                add_turn(chat_id, prompt, gpt_reply)

            except Exception as e:
                st.error(f"⚠️ AI 回覆失敗：{str(e)}")

