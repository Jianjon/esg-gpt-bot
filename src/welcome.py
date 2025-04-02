import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="ESG Service Path | 淨零小幫手", page_icon="🌱")
st.image("https://upload.wikimedia.org/wikipedia/commons/2/27/Leaf_icon_01.svg", width=60)
st.title("🌱 淨零小幫手 ESG Service Path")

st.markdown("""
歡迎使用 **淨零小幫手**，這是一套幫助企業了解自身永續現況的智能診斷工具。

本系統將透過您提供的資訊與問卷作答結果，
協助產出 ESG 現況分析、減碳建議與報告草稿。

👉 請填寫以下資訊後，點選下方按鈕開始診斷之旅。
""")

with st.form("user_info_form"):
    name = st.text_input("👤 您的姓名")
    email = st.text_input("📧 電子郵件（可選）")
    company = st.text_input("🏢 公司名稱")
    industry = st.selectbox("🏭 所屬產業類別", [
        "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
    ])
    start = st.form_submit_button("🚀 開始 ESG 初步診斷")

    if start:
        if not name or not company:
            st.warning("請填寫姓名與公司名稱後再開始診斷。")
        else:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.company_name = company
            st.session_state.industry = industry
            st.session_state.stage = "basic"
            st.switch_page("app.py")
