import streamlit as st
from dotenv import load_dotenv
import os
import json

def show_welcome_page():
    load_dotenv()

    st.markdown("""
    ## 👋 歡迎使用淨零小幫手

    這是一套幫助企業了解自身永續現況的智能診斷工具。  
    系統將根據您的背景與問卷作答，協助產出 ESG 現況分析、減碳建議與報告草稿。
    """)

    # ========== 基本資訊區塊 ==========
    st.markdown("#### 📜 請填寫您的基本資訊（必填）")
    with st.form("form_basic_info"):
        name = st.text_input("👤 您的姓名")
        email = st.text_input("📧 電子郵件")
        company = st.text_input("🏢 公司名稱")
        industry = st.selectbox("🏭 所屬產業類別", [
            "餐飲業", "旅宿業", "零售業", "小型製造業", "物流業", "辦公室服務業"
        ])
        reset_data = st.checkbox("🗑️ 我要重設所有回答紀錄（此動作無法還原）")
        start = st.form_submit_button("🚀 進入問卷調查")

    if start:
        if not name or not company:
            st.warning("請填寫姓名與公司名稱後再開始診斷。")
        else:
            # 儲存基本資料
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.company_name = company
            st.session_state.industry = industry
            st.session_state.reset_data = reset_data
            st.session_state.welcome_submitted = True

            session_file = os.path.join("data/sessions", f"{company}_{name}.json")
            os.makedirs(os.path.dirname(session_file), exist_ok=True)

            if reset_data and os.path.exists(session_file):
                os.remove(session_file)
                st.toast("✅ 已清除原有紀錄")

            st.rerun()  # ✅ 加這行強制刷新頁面

    # ========== 如果已提交基本資料，就顯示問卷 ==========
    if st.session_state.get("welcome_submitted") and not st.session_state.get("intro_survey_submitted"):
    # 顯示問卷調查表單（form_intro_survey）

        st.divider()
        st.markdown("## 🧠 ESG 問卷前導調查")

        with st.form("form_intro_survey"):
            survey_data = {}

            st.markdown("#### 1️⃣ **您對溫室氣體盤查的認知為何？**")
            survey_data["q1"] = st.radio("", [
                "完全不了解",
                "知道名稱但不熟內容",
                "知道概念但不熟實務",
                "曾經參與碳盤查",
                "非常熟悉並可教學"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 2️⃣ **您使用本系統的主要動機為？**")
            survey_data["q2"] = st.radio("", [
                "個人學習 ESG 知識",
                "幫助公司盤查與因應壓力",
                "準備考試或證照",
                "好奇試用"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 3️⃣ **您目前面臨哪些永續壓力？**")
            survey_data["q3"] = st.radio("", [
                "政府法規或稽查",
                "客戶或供應鏈要求",
                "內部 ESG 承諾或目標",
                "尚未感受到壓力"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 4️⃣ **您的角色或身分是？**")
            survey_data["q4"] = st.radio("", [
                "老闆 / 負責人",
                "永續專責 / 管理部門",
                "現場部門主管 / 員工",
                "顧問 / 教育人員",
                "學生或自由學習者"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 5️⃣ **您是否有 ESG 或碳盤查的相關經驗？**")
            survey_data["q5"] = st.radio("", [
                "完全沒有",
                "參加過課程但尚未實作",
                "有參與實作經驗",
                "協助完成過 ESG 報告",
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 6️⃣ **您最想學習的主題？**")
            survey_data["q6"] = st.radio("", [
                "碳盤查基礎概念",
                "產品碳足跡與標示",
                "減碳策略與範疇分類",
                "如何撰寫 ESG 報告",
                "永續採購與循環經濟"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 7️⃣ **您是否有產品碳足跡的相關需求？**")
            survey_data["q7"] = st.radio("", [
                "是，有客戶或通路要求",
                "還沒有，但將來可能需要",
                "沒有，暫不考慮"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 8️⃣ **您偏好的學習方式是？**")
            survey_data["q8"] = st.radio("", [
                "條列清楚、說明概念",
                "實際案例導入",
                "一步一步問答引導",
                "影片或圖解輔助",
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 9️⃣ **您希望系統如何回覆您的提問？**")
            survey_data["q9"] = st.radio("", [
                "簡單明瞭（不囉嗦）",
                "像老師引導學生那樣",
                "像顧問給策略建議那樣",
                "依照提問靈活調整"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("#### 🔟 **您希望系統給您怎樣的學習體驗？**")
            survey_data["q10"] = st.radio("", [
                "給我清楚答案與摘要就好",
                "用提問方式幫我思考",
                "循序漸進、一步步建立知識",
                "依照我目前程度推薦內容"
            ], label_visibility="collapsed")
            st.markdown("---")

            st.markdown("### 🗣️ 顧問語氣偏好設定")

            tone_choice = st.radio(
                "請選擇你偏好的顧問語氣風格：",
                options=[
                    ("gentle", "🌱 溫柔鼓勵型：親切包容，給人信心"),
                    ("professional", "🔍 專業分析型：邏輯清晰，強調重點"),
                    ("creative", "💡 創意思考型：鼓勵跳脫框架與創新")
                ],
                format_func=lambda x: x[1],  # 顯示文字
                index=0
            )

            # 儲存 tone 代碼
            st.session_state["preferred_tone"] = tone_choice[0]

            st.markdown("---")

            st.markdown("### 🧩 **請選擇您要進行的診斷階段：**")
            stage_choice = st.radio(
                "",
                ["初階問卷（僅含基本題:約30題）", "進階問卷（含全部題目:約60題）"],
                index=0
            , label_visibility="collapsed")

            submit = st.form_submit_button("🚀 開始 ESG 教學診斷")

            if submit:
                st.session_state["user_intro_survey"] = survey_data
                st.session_state["stage"] = "advanced" if stage_choice == "進階問卷（含全部題目）" else "basic"
                st.session_state["intro_survey_submitted"] = True
                st.success("✅ 問卷完成，即將進入診斷主流程")
                st.session_state["go_to_main"] = True
                st.rerun()

