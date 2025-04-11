import streamlit as st


def render_question_block(
    current_q: dict,
    current_index: int,
    rewritten_question: str = None,
) -> dict:
    """
    顯示問卷作答區塊（含 GPT 改寫說明、選項、自填欄位、三個按鈕）
    
    回傳：
        {
            "selected_options": List[str] 或 str,
            "custom_input": str,
            "back": bool,
            "forward": bool,
            "ask_ai": bool,
            "question_id": str,
        }
    """
    question_id = current_q.get("id", f"q{current_index}")
    option_type = current_q.get("option_type", "single")

    # 取得有效選項
    options = [
        ("A", current_q.get("option_A", "")),
        ("B", current_q.get("option_B", "")),
        ("C", current_q.get("option_C", "")),
        ("D", current_q.get("option_D", "")),
        ("E", current_q.get("option_E", "")),
    ]
    valid_options = [f"{key}. {text}" for key, text in options if text]

    # 顯示 GPT 改寫問題 or 原始問題
    st.markdown("### ❓ 本題問題")
    if rewritten_question:
        st.markdown(f"#### 🤖 顧問式提問")
        st.markdown(rewritten_question)
    else:
        st.markdown(current_q.get("question_text", "（無題目內容）"))

    with st.form(key=f"form_q_{question_id}"):
        # 顯示選項
        if option_type == "multi":
            selected_options = st.multiselect("請選擇適用的選項：", valid_options)
        else:
            selected_options = st.radio("請選擇最符合的選項：", valid_options)

        # 顯示自填欄位
        custom_input = st.text_input("若有補充，請在此輸入（選填）")

        # 三個按鈕
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            back = st.form_submit_button("⬅️ 上一題")
        with col2:
            forward = st.form_submit_button("➡️ 下一題")
        with col3:
            ask_ai = st.form_submit_button("🤖 詢問 AI 顧問")

    return {
        "selected_options": selected_options,
        "custom_input": custom_input,
        "back": back,
        "forward": forward,
        "ask_ai": ask_ai,
        "question_id": question_id
    }
__all__ = ["render_question_block"]
