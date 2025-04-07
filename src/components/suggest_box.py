import streamlit as st

def render_suggested_questions(suggested_list: list, submit_callback):
    """
    顯示建議問題按鈕，點選後自動送出問題。
    - suggested_list: 建議題目列表
    - submit_callback: 點選後執行的函式（會接收選到的問題為參數）
    """
    if not suggested_list:
        return

    cols = st.columns(len(suggested_list))
    for i, text in enumerate(suggested_list):
        label = f"💡 {text.strip()}"
        if cols[i].button(label, key=f"suggested_q_{i}"):
            submit_callback(text)
