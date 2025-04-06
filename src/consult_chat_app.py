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

def call_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    呼叫 GPT 模型，根據提供的 prompt 生成回應。
    Params:
        - prompt: 提供給 GPT 的文字提示
        - model: 使用的 GPT 模型（預設為 gpt-3.5-turbo）
    Return:
        - GPT 回應的文字
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位專業的 ESG 顧問，請用簡潔且實用的方式回答使用者問題。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ GPT 回應錯誤：{e}")
        return "抱歉，目前無法取得回覆，請稍後再試。"

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

    # 使用者輸入框
    user_input = st.text_input("你的回覆：", key=f"input_{session.current_index}")
    if user_input:
        st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        session.save_answer(user_input)

        # 記錄對話到 context_tracker
        context_tracker.add_turn(current_q["id"], user_input, "（AI 回覆待生成）")

        # 自動儲存進度
        save_to_json(session)

        # 下一題按鈕
        if st.button("👉 下一題"):
            # 自動摘要
            summary = context_tracker.update(current_q["id"], user_input)

            # 下一題
            session.advance()
            st.experimental_rerun()
else:
    st.success("問卷已完成！請點選下方按鈕產出診斷摘要報告。")
    if st.button("產出報告"):
        report = generate_basic_report(session.get_answers(), context_tracker.get_all_summaries())
        st.text_area("診斷報告：", report, height=400)

# ====== 引導式自由問答（進階支援）======
st.markdown("---")
st.subheader("需要幫助嗎？與顧問聊聊：")

from pathlib import Path
vector_path = Path("data/vector_output")
guided_rag = GuidedRAG(vector_path=vector_path)


if 'guided_chat' not in st.session_state:
    st.session_state['guided_chat'] = []
if 'guided_turns' not in st.session_state:
    st.session_state['guided_turns'] = 0

user_question = st.text_input("輸入你對此題的疑問，或直接輸入『不知道』：", key=f"help_{session.current_index}")

if user_question:
    st.session_state['guided_turns'] += 1
    st.session_state['guided_chat'].append(("user", user_question))

    ai_reply, related_chunks = guided_rag.ask(
        user_question,
        history=st.session_state['guided_chat'],
        turn=st.session_state['guided_turns']
    )

    st.markdown(f"<div class='ai-message'>{ai_reply}</div>", unsafe_allow_html=True)
    st.session_state['guided_chat'].append(("assistant", ai_reply))

    # 記錄對話到 context_tracker
    context_tracker.add_turn(current_q["id"], user_question, ai_reply)

    with st.expander("參考資料段落"):
        for chunk in related_chunks:
            st.markdown(f"**{chunk['source']}** - 第 {chunk['page']} 頁")
            st.markdown(f"> {chunk['text'][:300]}...\n")

    if st.session_state['guided_turns'] >= 3:
        st.info("這題若仍無法判斷，我們可以先進入下一題。")
        if st.button("跳過此題"):
            session.save_answer("（未回答）")
            context_tracker.update(current_q['id'], "未回答（由引導系統記錄）")
            session.advance()
            st.session_state['guided_turns'] = 0
            st.session_state['guided_chat'] = []
            st.experimental_rerun()
