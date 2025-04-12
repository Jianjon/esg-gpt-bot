# src/managers/profile_manager.py
import streamlit as st

def get_user_profile(user_id: str = "default") -> dict:
    """
    從 session_state 取得 ESG 前導問卷資料作為使用者 profile。
    """
    survey = st.session_state.get("user_intro_survey", {})

    return {
        "user_id": user_id,
        "user_name": st.session_state.get("user_name", "未命名"),
        "industry": st.session_state.get("industry", "未知產業"),
        "learning_stage": st.session_state.get("stage", "beginner"),
        "carbon_knowledge": survey.get("q1", ""),
        "esg_motivation": survey.get("q2", ""),
        "esg_pressure": survey.get("q3", ""),
        "role": survey.get("q4", ""),
        "experience": survey.get("q5", ""),
        "interest_topic": survey.get("q6", ""),
        "has_cf_need": survey.get("q7", "") == "是，有客戶或通路要求",
        "learning_style": survey.get("q8", ""),
        "answer_style": survey.get("q9", ""),
        "expectation": survey.get("q10", "")
    }
