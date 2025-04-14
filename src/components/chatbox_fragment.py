import streamlit as st
from sessions.context_tracker import get_conversation, add_turn
from src.utils.gpt_tools import call_gpt
from src.components.suggest_box import render_suggested_questions
from src.utils.topic_to_rag_map import get_rag_doc_for_question  # ✅ 新增：自動選擇向量庫

@st.fragment
def render_chatbox():

    if "session" not in st.session_state or not st.session_state.session:
        st.info("尚未載入問卷內容")
        return

    current_q = st.session_state.session.get_current_question()
    if not current_q:
        st.info("問卷已完成，無對話內容")
        return

    chat_id = current_q["id"]

    # 初始化已問清單
    if "asked_follow_ups" not in st.session_state:
        st.session_state["asked_follow_ups"] = set()

    # 對話容器
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # 顯示歷史紀錄
        for msg in get_conversation(chat_id):
            if "user" in msg:
                with st.chat_message("user"):
                    st.markdown(f" {msg['user']}")
            if "gpt" in msg:
                with st.chat_message("assistant"):
                    st.markdown(f" {msg['gpt']}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 自由輸入區
    prompt_key = f"chat_{chat_id}"
    if prompt := st.chat_input("針對本題還有什麼問題？可詢問 ESG 顧問 AI", key=prompt_key):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(f" {prompt}")
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("🔄 正在思考中...")

                rag_doc = get_rag_doc_for_question(current_q)  # ✅ 自動判斷對應的向量資料夾

                reply = call_gpt(
                    prompt=prompt,
                    question_text=current_q["text"],
                    learning_goal=current_q.get("learning_goal", ""),
                    chat_history=get_conversation(chat_id),
                    industry=st.session_state.get("industry", ""),
                    rag_doc=rag_doc
                )

                placeholder.markdown(f"🧑 {reply}")
                add_turn(chat_id, prompt, reply)
                st.session_state["asked_follow_ups"].add(prompt)
                st.session_state["_trigger_chat_fragment"] = st.session_state.get("_trigger_chat_fragment", 0) + 1
