import streamlit as st
import time
import json
from src.utils.prompt_builder import build_learning_prompt, generate_user_friendly_prompt
from src.utils.question_utils import get_previous_summary


def render_intro_block(current_q: dict, user_profile: dict, current_index: int, tone: str = "gentle"):
    from src.managers.guided_rag import GuidedRAG
    import time

    st.markdown('<div class="ai-intro-block">', unsafe_allow_html=True)

    if current_index == 0:
        st.markdown("#### 💬 AI 淨零顧問引導")

        if f"intro_text_q{current_q['id']}_first" not in st.session_state:
            st.session_state[f"intro_text_q{current_q['id']}_first"] = build_learning_prompt(
                tone=tone,
                is_first_question=True,
                user_profile=user_profile
            )

        for line in st.session_state[f"intro_text_q{current_q['id']}_first"].split("\n"):
            st.write(line.strip())
            time.sleep(0.3)

    else:
        st.markdown("#### 💬 AI 淨零顧問引導")

        if f"intro_text_q{current_q['id']}_summary" not in st.session_state:
            st.session_state[f"intro_text_q{current_q['id']}_summary"] = build_learning_prompt(
                tone=tone,
                is_first_question=False,
                previous_summary=get_previous_summary(current_q["id"]),
                user_profile=user_profile
            )

        for line in st.session_state[f"intro_text_q{current_q['id']}_summary"].split("\n"):
            st.write(line.strip())
            time.sleep(0.3)

        # 🎯 額外再顯示學習目標說明
        st.markdown("#### 🎯 本題學習目標說明")

        if f"friendly_q{current_q['id']}" not in st.session_state:
            rag = GuidedRAG(vector_path="data/vector_output/")
            rag_context = rag.query(current_q.get("learning_goal") or current_q.get("topic", ""))
            st.session_state[f"friendly_q{current_q['id']}"] = generate_user_friendly_prompt(
                current_q=current_q,
                user_profile=user_profile,
                rag_context=rag_context,
                tone=tone
            )

        for line in st.session_state[f"friendly_q{current_q['id']}"].split("\n"):
            st.write(line.strip())
            time.sleep(0.3)

    st.markdown('</div>', unsafe_allow_html=True)
