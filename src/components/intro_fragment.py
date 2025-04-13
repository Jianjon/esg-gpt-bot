# src/components/intro_fragment.py

import streamlit as st
from src.utils.prompt_builder import (
    build_intro_welcome_prompt,  # ✅ 僅用於第一題
    generate_user_friendly_prompt,
)
from src.managers.guided_rag import GuidedRAG
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

@st.fragment
def render_intro_fragment(current_q: dict, is_first_question: bool = False):
    qid = current_q["id"]
    tone = st.session_state.get("preferred_tone", "gentle")
    intro_key = f"intro_{qid}"
    goal_key = f"goal_note_{qid}"

    st.markdown("#### 💬 AI 淨零顧問引導")

    # ✅ 第一題才顯示歡迎導入
    if is_first_question and intro_key not in st.session_state:
        try:
            intro = build_intro_welcome_prompt(
                user_profile=user_profile,
                current_q=current_q,
                tone=tone
            )
            st.session_state[intro_key] = intro
        except Exception as e:
            st.session_state[intro_key] = f"❗導論產生失敗：{e}"

    if is_first_question:
        st.markdown(f"""<div class="ai-intro-box">{st.session_state[intro_key]}</div>""", unsafe_allow_html=True)

    # ✅ 每題都顯示學習目標（不管是不是第一題）
def render_intro_fragment(current_q: dict, is_first_question: bool = False, intro_prompt: str = None):
    qid = current_q["id"]
    tone = st.session_state.get("preferred_tone", "gentle")
    intro_key = f"intro_{qid}"
    goal_key = f"goal_note_{qid}"

    st.markdown("#### 💬 AI 淨零顧問引導")

    # ✅ 第一題才顯示歡迎導入
    if is_first_question and intro_key not in st.session_state:
        try:
            intro = build_intro_welcome_prompt(
                user_profile=user_profile,
                current_q=current_q,
                tone=tone
            )
            st.session_state[intro_key] = intro
        except Exception as e:
            st.session_state[intro_key] = f"❗導論產生失敗：{e}"

    if is_first_question:
        st.markdown(f"""<div class="ai-intro-box">{st.session_state[intro_key]}</div>""", unsafe_allow_html=True)

    # ✅ 每題學習目標說明：使用外部傳入的 intro_prompt（若有）優先
    if goal_key not in st.session_state:
        try:
            if intro_prompt:  # 🔥 使用預抓版本
                goal = intro_prompt
            else:
                rag = GuidedRAG("data/vector_output/")
                context = rag.query(current_q.get("learning_goal") or current_q.get("topic", ""))
                goal = generate_user_friendly_prompt(current_q, user_profile, context, tone)
            st.session_state[goal_key] = goal
        except Exception as e:
            st.session_state[goal_key] = f"⚠️ 學習目標補充失敗：{e}"

    st.markdown("#### 🎯 學習目標說明")
    st.markdown(f"""<div class="ai-intro-box">{st.session_state[goal_key]}</div>""", unsafe_allow_html=True)
