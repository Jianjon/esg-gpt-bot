import streamlit as st
import os
from pathlib import Path
from src.sessions.answer_session import AnswerSession
from src.loaders.question_loader import load_questions
from src.context.context_tracker import ContextTracker
from src.managers.report_generator import generate_report
from src.retriever.vector_guard import VectorStore
from src.managers.guided_rag import GuidedRAG
from openai import OpenAI
import openai
from src.managers.question_router import route_next_question
from src.managers.gpt_rewrite import rewrite_question_to_conversational

# 載入自訂樣式
def local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/custom_style.css")

st.set_page_config(page_title="ESG 顧問問答", layout="wide")
st.title("ESG 顧問式診斷問卷")

# 初始化狀態
if 'welcome_submitted' not in st.session_state or not st.session_state['welcome_submitted']:
    st.warning("請先完成產業選擇與公司基本資料填寫。")
    st.stop()

industry = st.session_state['industry']
stage = st.session_state.get('stage', 'basic')

questions = load_questions(industry, stage)
session = AnswerSession(questions)
tracker = ContextTracker()

# 顯示目前題目
current_q = session.get_current_question()
if current_q:
    st.markdown(
        f"<div class='fixed-question'>{current_q['text']}</div>",
        unsafe_allow_html=True
    )

    gpt_question = rewrite_question_to_conversational(current_q['text'])
    st.markdown(f"<div class='ai-message'>{gpt_question}</div>", unsafe_allow_html=True)

    user_input = st.text_input("你的回覆：", key=f"input_{session.current_index}")
    if user_input:
        st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        session.save_answer(user_input)
        summary = tracker.update(current_q['id'], user_input)
        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button("下一題"):
            session.advance()
            st.experimental_rerun()
else:
    st.success("問卷已完成！請點選下方按鈕產出診斷摘要報告。")
    if st.button("產出報告"):
        report = generate_report(session.get_answers(), tracker.get_summary())
        st.text_area("診斷報告：", report, height=400)

# ====== 引導式自由問答（進階支援）======
st.markdown("---")
st.subheader("需要幫助嗎？與顧問聊聊：")

vector_path = "data/vector_output"
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

    with st.expander("參考資料段落"):
        for chunk in related_chunks:
            st.markdown(f"**{chunk['source']}** - 第 {chunk['page']} 頁")
            st.markdown(f"> {chunk['text'][:300]}...\n")

    if st.session_state['guided_turns'] >= 3:
        st.info("這題若仍無法判斷，我們可以先進入下一題。")
        if st.button("跳過此題"):
            session.save_answer("（未回答）")
            tracker.update(current_q['id'], "未回答（由引導系統記錄）")
            session.advance()
            st.session_state['guided_turns'] = 0
            st.session_state['guided_chat'] = []
            st.experimental_rerun()
