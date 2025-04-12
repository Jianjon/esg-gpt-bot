import streamlit as st
from src.utils.prompt_builder import generate_dynamic_question_block, generate_option_notes
from src.utils.gpt_tools import call_gpt
from src.sessions.context_tracker import add_context_entry
from src.utils.session_saver import save_to_json
from streamlit import rerun


@st.fragment
def render_questionnaire_fragment():
    if "session" not in st.session_state:
        st.warning("⚠️ 尚未載入問卷資料，請重新載入或回到歡迎頁。")
        return

    session = st.session_state.session
    current_q = session.get_current_question()
    if not current_q:
        st.success("🎉 您已完成本階段問卷！")
        return

    user_profile = st.session_state.get("user_intro_survey", {})
    qid = current_q["id"]

    # === 題目導論快取 ===
    intro_key = f"gpt_question_intro_{qid}"
    if intro_key not in st.session_state:
        try:
            prompt = generate_dynamic_question_block(
                user_profile=user_profile,
                current_q=current_q,
                user_answer=""
            )
            gpt_response = call_gpt(prompt)
        except Exception as e:
            gpt_response = f"⚠️ 無法產生題目導論：{e}"
        st.session_state[intro_key] = gpt_response

    st.markdown("### 📝 題目引導說明")
    st.markdown(st.session_state[intro_key])

    # === 選項說明補充（如果原本的註解是空的）===
    option_notes = current_q.get("option_notes", {})
    if all(not note for note in option_notes.values()):
        try:
            opt_prompt = generate_option_notes(current_q)
            notes_response = call_gpt(opt_prompt)
            lines = notes_response.splitlines()
            new_notes = {opt: line.strip("- ").strip() for opt, line in zip(current_q["options"], lines)}
            current_q["option_notes"] = new_notes
        except Exception as e:
            st.warning(f"⚠️ 無法補充選項說明：{e}")

    # === 顯示選項 ===
    options = current_q["options"]
    option_notes = current_q.get("option_notes", {})
    formatted_options = [f"{opt}：{option_notes.get(opt, '')}" for opt in options]
    selected = []

    if current_q["type"] == "single":
        selected_html = st.radio(
            "可選擇：", formatted_options, format_func=lambda x: x, key=f"radio_{qid}"
        )
        if selected_html:
            selected = [options[formatted_options.index(selected_html)]]
    else:
        st.markdown("可複選：")
        for i, html in enumerate(formatted_options):
            opt_key = options[i]
            if st.checkbox(html, key=f"checkbox_{qid}_{opt_key}"):
                selected.append(opt_key)

    # === 自訂答案輸入 ===
    custom_input = ""
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input(
            label="請輸入內容",
            placeholder="自訂作答 (可填寫您的作法)...",
            key=f"custom_{qid}"
        )
        if custom_input:
            selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]

    # === 導覽按鈕 ===
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 上一題", key=f"prev_{qid}"):
            session.go_back()
            st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1
            rerun()

    with col2:
        if st.button("➡️ 下一題（提交答案）", key=f"next_{qid}"):
            if not selected:
                st.warning("⚠️ 請先選擇或填寫一個答案後再繼續")
                return

            answer_payload = selected[0] if current_q["type"] == "single" else selected
            result = session.submit_response(answer_payload)
            add_context_entry(qid, answer_payload, current_q["text"])
            save_to_json(session)

            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1
                st.success("✅ 已提交，即將跳轉至下一題")
                rerun()
