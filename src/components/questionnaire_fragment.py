# src/components/questionnaire_fragment.py

import streamlit as st
from src.utils.prompt_builder import (
    build_learning_prompt,
    generate_option_notes,
    generate_user_friendly_prompt,
)
from src.utils.gpt_tools import call_gpt
from src.utils.question_utils import get_previous_summary
from src.utils.session_saver import save_to_json
from src.managers.guided_rag import GuidedRAG
from streamlit import rerun
from src.sessions.context_tracker import add_context_entry
from src.sessions.context_tracker import generate_following_action
from src.utils.prompt_builder import generate_dynamic_question_block
from src.utils.prompt_builder import generate_option_notes
from src.managers.profile_manager import get_user_profile
user_profile = get_user_profile()

if "_trigger_all_sections" not in st.session_state:
    st.session_state["_trigger_all_sections"] = 0
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

    qid = current_q["id"]
    ready_flag = f"q{qid}_ready"
    selected_key = f"selected_{qid}"

    if ready_flag not in st.session_state:
        st.session_state[ready_flag] = False
    if selected_key not in st.session_state:
        st.session_state[selected_key] = []

    user_profile = get_user_profile()
    tone = st.session_state.get("preferred_tone", "gentle")
    current_index = session.current_index

    # === 區塊一：導論區（僅顯示一次） ===
    if not st.session_state[ready_flag]:
        st.markdown("#### 💬 AI 淨零顧問引導")
        try:
            summary = get_previous_summary(qid)
            intro = build_learning_prompt(
                tone=tone,
                previous_summary=summary,
                is_first_question=(current_index == 0),
                current_q=current_q,
                user_profile=user_profile
            )
            st.markdown("#### 📌 本題重點：" + current_q.get("text", ""))
            st.markdown(f"""<div class="ai-intro-box">{intro}</div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❗導論產生失敗：{e}")

        st.markdown("#### 🎯 學習目標說明")
        try:
            rag = GuidedRAG("data/vector_output/")
            context = rag.query(current_q.get("learning_goal") or current_q.get("topic", ""))
            explain = generate_user_friendly_prompt(
                current_q=current_q,
                user_profile=user_profile,
                rag_context=context,
                tone=tone
            )
            st.markdown(f"""<div class="ai-intro-box">{explain}</div>""", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ 學習目標補充失敗：{e}")

        with st.form(f"ready_form_{qid}"):
            if st.form_submit_button("✅ 我準備好了，開始作答"):
                st.session_state[ready_flag] = True
        return

    # === 區塊二：作答區 ===
    try:
        guide = generate_dynamic_question_block(
            user_profile=user_profile,
            current_q=current_q,
            tone=tone
        )
        st.markdown(f"""<div class="ai-intro-box">{guide}</div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ 題目導引產生失敗：{e}")

    try:
        rewritten_notes = generate_option_notes(current_q, user_profile, tone)
    except Exception as e:
        rewritten_notes = {opt: f"⚠️ 無法產生說明：{e}" for opt in current_q.get("options", [])}

    options = current_q["options"]
    formatted_options = [f"{opt}：{rewritten_notes.get(opt, '')}" for opt in options]
    selected = st.session_state.get(selected_key, [])

    # 單選題邏輯
    if current_q["type"] == "single":
        selected_html = st.radio(
            "可選擇：", formatted_options,
            index=formatted_options.index(f"{selected[0]}：{rewritten_notes.get(selected[0], '')}") if selected else 0,
            key=f"radio_{qid}",
        )
        if selected_html:
            selected = [options[formatted_options.index(selected_html)]]
            st.session_state[selected_key] = selected

    # 複選題邏輯
    else:
        st.markdown("可複選：")
        for i, html in enumerate(formatted_options):
            cb_key = f"checkbox_{qid}_{options[i]}"
            if st.checkbox(html, key=cb_key, value=options[i] in selected):
                if options[i] not in selected:
                    selected.append(options[i])
            elif options[i] in selected:
                selected.remove(options[i])
        st.session_state[selected_key] = selected

    # 自訂作答
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input("請輸入內容", key=f"custom_{qid}")
        if custom_input:
            selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]
            st.session_state[selected_key] = selected

    # --- 下一題 / 上一題按鈕 ---
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 上一題", key=f"prev_{qid}"):
            session.go_back()

    with col2:
        if st.button("➡️ 下一題（提交答案）", key=f"next_{qid}"):
            if not selected:
                st.warning("⚠️ 請先作答再繼續")
                return
            result = session.submit_response(selected)
            add_context_entry(qid, selected, current_q["text"])
            save_to_json(session)

            try:
                full_answer = "、".join(selected) if isinstance(selected, list) else selected
                suggestion = generate_following_action(current_q=current_q, user_answer=full_answer, user_profile=user_profile)
            except Exception as e:
                suggestion = f"⚠️ 無法產生建議：{e}"
            st.toast(f"💡 下一步建議：{suggestion}")

            if "error" in result:
                st.error(result["error"])
            else:
                session.go_forward()
