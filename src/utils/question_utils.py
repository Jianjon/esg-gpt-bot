# src/utils/question_utils.py

import streamlit as st

def get_previous_summary(current_qid: str) -> str:
    """
    根據目前題目 ID，回傳上一題的 GPT 總結摘要（若有）。
    資料來自 session_state["context_history"]，預設為空字串。
    """
    summaries = st.session_state.get("context_history", [])
    session = st.session_state.get("session")
    if not session or not current_qid:
        return ""

    # 取得目前題目 index
    try:
        current_index = next(i for i, q in enumerate(session.question_set) if q["id"] == current_qid)
    except StopIteration:
        return ""

    # 若為第一題則無前一題摘要
    if current_index == 0:
        return ""

    # 找出上一題 ID 與對應摘要
    prev_qid = session.question_set[current_index - 1]["id"]
    prev_summary = next((s["summary"] for s in summaries if s["id"] == prev_qid), "")

    return prev_summary
