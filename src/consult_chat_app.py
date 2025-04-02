import streamlit as st
from loaders.question_loader import load_questions
from sessions.answer_session import AnswerSession
from sessions.context_tracker import add_context_entry, get_all_summaries
from openai import OpenAI
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="ESG 顧問對談模式", page_icon="💬")
st.title("💬 淨零小幫手｜ESG 顧問對談模式")

# 初始使用者狀態
if "user_name" not in st.session_state or "industry" not in st.session_state:
    st.warning("請先從 welcome.py 進入，輸入基本資訊。")
    st.stop()

if "stage" not in st.session_state:
    st.session_state.stage = "basic"

# 載入題庫
industry = st.session_state.industry
questions = load_questions(industry, st.session_state.stage)

# 問卷 session 初始化
if "consult_session" not in st.session_state:
    st.session_state.consult_session = AnswerSession(
        user_id=st.session_state.user_name,
        question_set=questions
    )

session = st.session_state.consult_session
current_q = session.get_current_question()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 對話開始
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if current_q:
    # 使用 GPT 生成顧問語氣提問
    q_prompt = f"你是一位 ESG 顧問，請以親切、專業、顧問式語氣，根據以下題目設計一段自然語言提問：\n題目：{current_q['text']}"

    gpt_question = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一位熟悉碳盤查與 ESG 的企業顧問，擅長將問卷問題轉為人性化提問。"},
            {"role": "user", "content": q_prompt}
        ]
    )["choices"][0]["message"]["content"].strip()

    with st.chat_message("assistant"):
        st.markdown(gpt_question)
    st.session_state.chat_history.append({"role": "assistant", "content": gpt_question})

    user_input = st.chat_input("請輸入您的回答...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 提交回答並進入下一題
        session.submit_response(user_input)
        add_context_entry(current_q["id"], user_input, current_q["text"])
        st.rerun()
else:
    with st.chat_message("assistant"):
        st.success("✅ 所有問題皆已完成，感謝您的分享！")
        st.markdown("### 回顧摘要：")
        for summary in get_all_summaries():
            st.markdown(f"- {summary}")
