import streamlit as st
from src.utils.prompt_builder import generate_dynamic_question_block
from src.utils.gpt_tools import call_gpt
from src.sessions.context_tracker import add_context_entry
from src.utils.session_saver import save_to_json
from streamlit import rerun


@st.fragment
def render_questionnaire():
    session = st.session_state.session
    current_q = session.get_current_question()
    if not current_q:
        st.success("🎉 您已完成本階段問卷！")
        return

    # === 題目標題與說明（快取處理）===
    cache_key = f"gpt_question_intro_{current_q['id']}"
    if cache_key not in st.session_state:
        dynamic_prompt = generate_dynamic_question_block(
            user_profile=st.session_state.get("user_intro_survey", {}),
            current_q=current_q,
            user_answer=""
        )
        try:
            gpt_response = call_gpt(dynamic_prompt)
            parts = gpt_response.split("【說明】")
            question_title = parts[0].replace("【題目】", "").strip()
            question_intro = parts[1].strip()
        except Exception:
            question_title = current_q.get("text", "")
            question_intro = current_q.get("question_note", "")
        st.session_state[cache_key] = {"title": question_title, "intro": question_intro}

    question_title = st.session_state[cache_key]["title"]
    question_intro = st.session_state[cache_key]["intro"]

    # === 顯示標題與引導說明 ===
    st.markdown("### 📝 題目")
    st.markdown(f"<p style='font-size:18px'><strong>{question_title}</strong></p>", unsafe_allow_html=True)
    st.markdown("#### 🗒️ 題目說明")
    st.markdown(f"<div style='font-size:16px'>{question_intro}</div>", unsafe_allow_html=True)

    # === 顯示選項 ===
    options = current_q["options"]
    option_notes = current_q.get("option_notes", {})
    formatted_options = [f"{opt}：{option_notes.get(opt, '')}" for opt in options]
    selected = []

    if current_q["type"] == "single":
        selected_html = st.radio(
            "可選擇：", formatted_options, format_func=lambda x: x, key=f"radio_{current_q['id']}"
        )
        if selected_html:
            selected = [options[formatted_options.index(selected_html)]]
    else:
        st.markdown("可複選：")
        for i, html in enumerate(formatted_options):
            opt_key = options[i]
            if st.checkbox(html, key=f"checkbox_{current_q['id']}_{opt_key}"):
                selected.append(opt_key)

    # === 自訂答案輸入 ===
    custom_input = ""
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input(
            label="請輸入內容",
            placeholder="自訂作答 (可填寫您的作法)...",
            key=f"custom_{current_q['id']}"
        )
        if custom_input:
            selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]

    # === 導航按鈕區塊 ===
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 上一題", key=f"prev_{current_q['id']}"):
            session.go_back()
            st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1
            rerun()

    with col2:
        if st.button("➡️ 下一題（提交答案）", key=f"next_{current_q['id']}"):
            if not selected:
                st.warning("⚠️ 請先選擇或填寫一個答案後再繼續")
                return

            answer_payload = selected[0] if current_q["type"] == "single" else selected
            result = session.submit_response(answer_payload)
            add_context_entry(current_q["id"], answer_payload, current_q["text"])
            save_to_json(session)

            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1
                st.success("✅ 已提交，即將跳轉至下一題")
                rerun()
