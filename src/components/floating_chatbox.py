# src/components/floating_chatbox.py
import streamlit as st
from src.utils.gpt_tools import call_gpt


@st.fragment
def render_floating_chatbox(question_id: str):
    chat_key = f"qa_threads_{question_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    if "_chat_input" not in st.session_state:
        st.session_state["_chat_input"] = ""

    st.markdown(chatbox_css(), unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="chatbox-container">', unsafe_allow_html=True)

        # --- 顯示歷史對話（舊的在上，新的在下）---
        for turn in st.session_state[chat_key]:
            role_class = "chat-bubble-user" if turn["role"] == "user" else "chat-bubble-assistant"
            st.markdown(f"""
                <div class="{role_class}">
                    {turn["content"]}
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # --- 輸入框 ---
        user_input = st.chat_input("你想問什麼？", key="chat_input")
        if user_input:
            st.session_state[chat_key].append({"role": "user", "content": user_input})
            response = call_gpt(user_input)
            st.session_state[chat_key].append({"role": "assistant", "content": response})
            st.session_state["_trigger_chat_refresh"] += 1  # ✅ 觸發聊天 fragment 更新


def chatbox_css():
    return """
    <style>
    .chatbox-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 360px;
        max-height: 420px;
        padding: 16px;
        background-color: #f7f9fc;
        border: 1px solid #ddd;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        overflow-y: auto;
        z-index: 9999;
    }
    .chat-bubble-user {
        background-color: #dcfce7;
        color: #000;
        padding: 8px 12px;
        border-radius: 16px;
        margin-bottom: 8px;
        text-align: right;
        font-size: 14px;
    }
    .chat-bubble-assistant {
        background-color: #e2e8f0;
        color: #000;
        padding: 8px 12px;
        border-radius: 16px;
        margin-bottom: 8px;
        text-align: left;
        font-size: 14px;
    }
    </style>
    """
