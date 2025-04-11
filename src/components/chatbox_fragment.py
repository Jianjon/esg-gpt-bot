import streamlit as st
from sessions.context_tracker import get_conversation, add_turn
from src.utils.gpt_tools import call_gpt
from src.components.suggest_box import render_suggested_questions


@st.fragment
def render_chatbox():
    st.markdown("#### 🤖 淨零小幫手（測試階段以五題為限）")

    if "session" not in st.session_state or not st.session_state.session:
        st.info("尚未載入問卷內容")
        return

    current_q = st.session_state.session.get_current_question()
    if not current_q:
        st.info("問卷已完成，無對話內容")
        return

    chat_id = current_q["id"]

    # 對話容器（LINE 風格樣式）
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for msg in get_conversation(chat_id):
            if "user" in msg:
                with st.chat_message("user"):
                    st.markdown(msg["user"])
            if "gpt" in msg:
                with st.chat_message("assistant"):
                    st.markdown(msg["gpt"])

        st.markdown('</div>', unsafe_allow_html=True)

    # 顯示建議問題按鈕（由 render_suggested_questions 控制）
    suggested_prompts_raw = current_q.get("follow_up", "")
    all_suggested_prompts = [s.strip() + "？" for s in suggested_prompts_raw.split("？") if s.strip()]

    if "asked_follow_ups" not in st.session_state:
        st.session_state["asked_follow_ups"] = set()

    suggested_prompts = [p for p in all_suggested_prompts if p not in st.session_state["asked_follow_ups"]]
    render_suggested_questions(suggested_prompts)

    # ✅ 若有使用者點擊建議問題，就執行回覆
    selected = st.session_state.pop("submit_suggested_question", None)
    if selected:
        with chat_container:
            with st.chat_message("user"):
                st.markdown(selected)
            with st.chat_message("assistant"):
                with st.spinner("AI 回覆中..."):
                    reply = call_gpt(
                        prompt=selected,
                        question_text=current_q["text"],
                        learning_goal=current_q.get("learning_goal", ""),
                        chat_history=get_conversation(chat_id),
                        industry=st.session_state.get("industry", "")
                    )
                    st.markdown(reply)
                    add_turn(chat_id, selected, reply)
                    st.session_state["asked_follow_ups"].add(selected)
                    st.session_state["_trigger_chat_fragment"] = st.session_state.get("_trigger_chat_fragment", 0) + 1

    # 使用者自由輸入
    if prompt := st.chat_input("針對本題還有什麼問題？可詢問 ESG 顧問 AI", key=f"chat_{chat_id}"):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI 回覆中..."):
                    reply = call_gpt(
                        prompt=prompt,
                        question_text=current_q["text"],
                        learning_goal=current_q.get("learning_goal", ""),
                        chat_history=get_conversation(chat_id),
                        industry=st.session_state.get("industry", "")
                    )
                    st.markdown(reply)
                    add_turn(chat_id, prompt, reply)
                    st.session_state["asked_follow_ups"].add(prompt)
                    st.session_state["_trigger_chat_fragment"] = st.session_state.get("_trigger_chat_fragment", 0) + 1
