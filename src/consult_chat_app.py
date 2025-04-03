import streamlit as st
import os
from src.sessions.answer_session import AnswerSession
from src.loaders.question_loader import load_questions
from src.context.context_tracker import ContextTracker
from src.managers.report_generator import generate_report
from src.retriever.vector_guard import check_vector_store_exists

from openai import OpenAIError
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

    # 顯示轉換後的顧問式提問語氣
    gpt_question = rewrite_question_to_conversational(current_q['text'])
    st.markdown(f"<div class='ai-message'>{gpt_question}</div>", unsafe_allow_html=True)

    # 使用者回答區
    user_input = st.text_input("你的回覆：", key=f"input_{session.current_index}")
    if user_input:
        st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        session.save_answer(user_input)
        summary = tracker.update(current_q['id'], user_input)
        st.markdown("<hr>", unsafe_allow_html=True)

        # 顯示下一題按鈕
        if st.button("下一題"):
            session.advance()
            st.experimental_rerun()
else:
    st.success("問卷已完成！請點選下方按鈕產出診斷摘要報告。")
    if st.button("產出報告"):
        report = generate_report(session.get_answers(), tracker.get_summary())
        st.text_area("診斷報告：", report, height=400)

# 自由問答區（若有向量庫）
if check_vector_store_exists():
    st.markdown("---")
    st.subheader("自由提問")
    custom_question = st.text_input("你想詢問的其他 ESG 問題是？")
    if custom_question:
        st.markdown(f"<div class='user-message'>{custom_question}</div>", unsafe_allow_html=True)
        # TODO: 呼叫 RAG 回答並呈現
        st.markdown(f"<div class='ai-message'>這是未來的回答示意。</div>", unsafe_allow_html=True)
else:
    st.info("目前尚未建立向量資料庫，無法使用自由問答功能。")
