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

    # ✅ 新增這段：初始化每題的 ready flag，預設為 False（還沒準備好）
    qid = current_q["id"]
    ready_flag = f"q{qid}_ready"
    if ready_flag not in st.session_state:
        st.session_state[ready_flag] = False

    user_profile = st.session_state.get("user_intro_survey", {})
    tone = st.session_state.get("preferred_tone", "gentle")
    current_index = session.current_index

    # === 第一段：顧問導論 + 學習目標 + 準備按鈕 ===
    if not st.session_state.get(ready_flag, False):
        st.markdown("#### 💬 AI 淨零顧問引導")
        try:
            summary = get_previous_summary(qid)
            is_first = current_index == 0
            intro_text = build_learning_prompt(
                tone=tone,
                previous_summary=summary,
                is_first_question=is_first,
                current_q=current_q,
                user_profile=user_profile
            )

            st.markdown(f"""<div class="ai-intro-box">{intro_text}</div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ 無法產生導論語句：{e}")

        st.markdown("#### 🎯 本題學習目標說明")
        try:
            rag = GuidedRAG(vector_path="data/vector_output/")
            rag_context = rag.query(current_q.get("learning_goal") or current_q.get("topic", ""))
            learning_prompt = generate_user_friendly_prompt(
                current_q=current_q,
                user_profile=user_profile,
                rag_context=rag_context,
                tone=tone
            )
            st.markdown(f"""<div class="ai-intro-box">{learning_prompt}</div>""", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ 無法補充學習目標說明：{e}")

        # === 按下「我準備好了」 ===
        with st.form(key=f"ready_form_{qid}"):
            submitted = st.form_submit_button("✅ 我準備好了，開始作答")
            if submitted:
                st.session_state[ready_flag] = True
                rerun()
        return

    # === 第二段：作答區 ===
    try:
        rewritten_notes = generate_option_notes(
            current_q=current_q,
            user_profile=user_profile,
            tone=tone
        )
    except Exception as e:
        rewritten_notes = {
            opt: f"⚠️ 無法產生說明：{e}" for opt in current_q.get("options", [])
        }

    options = current_q["options"]
    formatted_options = [
        f"{opt}：{rewritten_notes.get(opt, '')}" for opt in options
    ]
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

    custom_input = ""
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input(
            label="請輸入內容",
            placeholder="自訂作答 (可填寫您的作法)...",
            key=f"custom_{qid}"
        )
        if custom_input:
            selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]

    # === 上一題 / 下一題按鈕 ===
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

            try:
                full_answer = "、".join(answer_payload) if isinstance(answer_payload, list) else answer_payload
                suggestion = generate_following_action(
                    current_q=current_q,
                    user_answer=full_answer,
                    user_profile=user_profile
                )
            except Exception as e:
                suggestion = f"⚠️ 無法產生建議：{e}"

            st.toast(f"💡 下一步建議：{suggestion}")

            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state["_trigger_all_sections"] += 1
                st.success("✅ 已提交，即將跳轉至下一題")
                rerun()
