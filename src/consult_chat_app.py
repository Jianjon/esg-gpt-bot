import streamlit as st
import os
from pathlib import Path
from src.sessions.answer_session import AnswerSession
from src.loaders.question_loader import load_questions
from src.context.context_tracker import ContextTracker
from src.managers.report_generator import generate_report
from src.retriever.vector_guard import VectorStore
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

# ====== 自由問答區（RAG 整合）======
st.markdown("---")
st.subheader("自由提問")

vector_store = VectorStore()
vector_path = Path("data/vector_output")

if not vector_store.exists(vector_path):
    st.info("目前尚未建立向量資料庫，無法使用自由問答功能。")
    st.stop()
else:
    vector_store.load(vector_path)
    custom_question = st.text_input("你想詢問的其他 ESG 問題是？")

    if custom_question:
        st.markdown(f"<div class='user-message'>{custom_question}</div>", unsafe_allow_html=True)

        # 搜尋相關段落
        similar_chunks = vector_store.search(custom_question, top_k=5)

        # 整理作為 context 傳給 GPT
        context_text = "\n\n".join([chunk['text'] for chunk in similar_chunks])

        system_prompt = """
你是一位熟悉 ESG 與碳盤查的顧問，請根據以下知識段落回答使用者的問題。
若無相關資訊，請誠實說明。請使用條列式清楚回答。

以下是參考資料：
""" + context_text

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": custom_question}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.3
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(f"<div class='ai-message'>{answer}</div>", unsafe_allow_html=True)

            with st.expander("查看引用段落"):
                for chunk in similar_chunks:
                    st.markdown(f"**{chunk['source']}** - 第 {chunk['page']} 頁")
                    st.markdown(f"> {chunk['text'][:300]}...\n")
        except Exception as e:
            st.error(f"❌ 查詢失敗：{str(e)}")
