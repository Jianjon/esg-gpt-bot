import streamlit as st
from dotenv import load_dotenv
import os

def show_welcome():
    # 載入 .env 環境變數
    load_dotenv()

    # 頁面設定
    # st.set_page_config(page_title="ESG Service Path | 淨零小幫手", page_icon="🌱")
    # st.title("🌱 淨零小幫手 ESG Service Path")

    st.markdown("""
    歡迎使用 **淨零小幫手**，這是一套幫助企業了解自身永續現況的智能診斷工具。

    本系統將透過您提供的資訊與問卷作答結果，
    協助產出 ESG 現況分析、減碳建議與報告草稿。
    """)

    with st.form("user_info_form"):
        name = st.text_input("👤 您的姓名")
        email = st.text_input("📧 電子郵件（可選）")
        company = st.text_input("🏢 公司名稱")
        industry = st.selectbox("🏭 所屬產業類別", [
            "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
        ])
        reset_data = st.checkbox("🗑️ 我要重設所有回答紀錄（此動作無法還原）")

        st.markdown("---")
        st.markdown("### 🧩 請選擇您要進行的診斷階段：")

        stage_choice = st.radio(
            "您希望從哪個階段開始？",
            ["初階問卷（僅含基本題）", "進階問卷（含全部題目）"],
            index=0
        )

        stage = "advanced" if stage_choice == "進階問卷（含全部題目）" else "basic"

        start = st.form_submit_button("🚀 開始 ESG 問卷診斷")

        if start:
            if not name or not company:
                st.warning("請填寫姓名與公司名稱後再開始診斷。")
            else:
                st.session_state.user_name = name
                st.session_state.user_email = email
                st.session_state.company_name = company
                st.session_state.industry = industry
                st.session_state.stage = stage
                st.session_state.reset_data = reset_data

                session_file = os.path.join("data/sessions", f"{company}_{name}.json")
                if reset_data and os.path.exists(session_file):
                    os.remove(session_file)
                    st.toast("✅ 已清除原有紀錄，問卷將從頭開始。")

                st.success("✅ 基本資訊完成，正在進入問卷頁面...")
                st.rerun()
