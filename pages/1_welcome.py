# 📄 welcome.py
import streamlit as st
from dotenv import load_dotenv
import os
import json

st.set_page_config(page_title="歡迎使用淨零小幫手", page_icon="🌱")
load_dotenv()

st.markdown("""
## 👋 歡迎使用淨零小幫手

這是一套幫助企業了解自身永續現況的智能診斷工具。  
系統將根據您的背景與問卷作答，協助產出 ESG 現況分析、減碳建議與報告草稿。
""")

st.markdown("### 📝 請填寫您的基本資訊（必填）")
with st.form("user_info_form"):
    name = st.text_input("👤 您的姓名")
    email = st.text_input("📧 電子郵件（可選）")
    company = st.text_input("🏢 公司名稱")
    industry = st.selectbox("🏭 所屬產業類別", [
        "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
    ])
    reset_data = st.checkbox("🗑️ 我要重設所有回答紀錄（此動作無法還原）")
    start = st.form_submit_button("🚀 進入問卷填寫")

    if start:
        if not name or not company:
            st.warning("請填寫姓名與公司名稱後再開始診斷。")
        else:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.company_name = company
            st.session_state.industry = industry
            st.session_state.reset_data = reset_data
            st.session_state.welcome_submitted = True

            # 預儲 session 檔案（預設路徑）
            session_file = os.path.join("data/sessions", f"{company}_{name}.json")
            os.makedirs(os.path.dirname(session_file), exist_ok=True)

            if reset_data and os.path.exists(session_file):
                os.remove(session_file)
                st.toast("✅ 已清除原有紀錄")

            st.success("✅ 基本資訊完成，正在進入問卷頁面...")
            st.switch_page("intro_survey")  # ✅ 進入第二頁
