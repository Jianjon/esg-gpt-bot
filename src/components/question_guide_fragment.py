# src/components/question_guide_fragment.py

import streamlit as st
from src.utils.prompt_builder import (
    generate_dynamic_question_block,
    generate_option_notes,
)
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

@st.fragment  # ⚠️ 已更新為非 experimental
def render_question_guide(current_q: dict):
    qid = current_q["id"]
    tone = st.session_state.get("preferred_tone", "gentle")

    st.markdown(f"#### 📌 本題重點：{current_q.get('text', '')}")

    # ✅ 題目導引（快取）
    guide_key = f"guide_{qid}"
    if guide_key not in st.session_state:
        try:
            guide = generate_dynamic_question_block(user_profile, current_q, tone)
            st.session_state[guide_key] = guide
        except Exception as e:
            st.session_state[guide_key] = f"⚠️ 題目導引產生失敗：{e}"

    st.markdown(f"""<div class="ai-intro-box">{st.session_state[guide_key]}</div>""", unsafe_allow_html=True)

    # ✅ 選項補充說明快取（僅快取，不顯示）
    notes_key = f"option_notes_{qid}"
    if (
        notes_key not in st.session_state
        or not isinstance(st.session_state[notes_key], dict)
        or len(st.session_state[notes_key]) == 0
    ):
        try:
            notes = generate_option_notes(current_q, user_profile, tone)
            st.session_state[notes_key] = notes
        except Exception as e:
            st.session_state[notes_key] = {
                opt: f"⚠️ 無法產生說明：{e}" for opt in current_q.get("options", [])
            }
