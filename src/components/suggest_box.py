import streamlit as st

def render_suggested_questions(suggested_list: list, session_key: str = "submit_suggested_question"):
    """
    顯示建議問題按鈕，點選後儲存選項，讓外層 callback 處理（避免 Fragment rerun 錯誤）
    - suggested_list: 建議題目列表
    - session_key: 被點選後暫存問題的 key，預設為 "submit_suggested_question"
    """
    if not suggested_list:
        return

    if "clicked_prompts" not in st.session_state:
        st.session_state["clicked_prompts"] = set()

    cols = st.columns(len(suggested_list))
    for i, text in enumerate(suggested_list):
        key = f"suggested_q_{i}"
        label = f"💡 {text.strip()}"

        if text in st.session_state["clicked_prompts"]:
            cols[i].button(label, key=key, disabled=True)
        else:
            if cols[i].button(label, key=key):
                st.session_state["clicked_prompts"].add(text)
                st.session_state[session_key] = text  # ✅ 記錄點擊事件（由外層判斷執行）
