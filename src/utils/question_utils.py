# src/utils/question_utils.py

import streamlit as st


def get_previous_summary(current_qid: str) -> str:
    """
    根據目前題目 ID，回傳上一題的 GPT 總結摘要（若有）。
    資料來自 session_state["context_history"]
    """
    summaries = st.session_state.get("context_history", [])
    session = st.session_state.get("session")
    if not session:
        return ""

    # 取得上一題的 ID
    idx = next((i for i, q in enumerate(session.question_set) if q["id"] == current_qid), None)
    if idx is None or idx == 0:
        return ""

    prev_qid = session.question_set[idx - 1]["id"]
    match = next((s for s in summaries if s["id"] == prev_qid), None)
    return match["summary"] if match else ""
