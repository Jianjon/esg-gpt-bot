# src/components/floating_chatbox.py
import streamlit as st
from streamlit_float import float_init


def render_floating_chatbox(question_id: str):
    float_init()  # 初始化浮動功能

    # 對話視窗容器
    with st.container():
        st.markdown("#### 🤖 AI 顧問小視窗")
        chat_key = f"qa_threads_{question_id}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        for turn in st.session_state[chat_key]:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

        user_input = st.chat_input("你想問什麼？")
        if user_input:
            st.session_state[chat_key].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # GPT 回覆（這裡你可以改成 call_gpt 或其他邏輯）
            from src.utils.gpt_tools import call_gpt
            response = call_gpt(user_input)
            st.session_state[chat_key].append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

    # 使用 streamlit-float 定位右下角
# 假設你是在用 st.markdown 或 st.components.v1.html 自訂 CSS：
st.markdown("""
    <style>
    .floating-chatbox {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)
