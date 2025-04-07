# 📄 user_intro_survey.py

import streamlit as st

def show_intro_survey_page():
    st.markdown("## 🧠 ESG 問卷前導調查")
    st.markdown("""
在進行 ESG 智能診斷前，我們會先了解您的背景、動機與學習偏好，以提供更貼近的建議與回應方式。
請依據您的實際狀況作答：
""")

survey_data = {}

survey_data["q1"] = st.radio("1️⃣ 您對溫室氣體盤查的認知為何？", [
    "完全不了解",
    "知道名稱但不熟內容",
    "知道概念但不熟實務",
    "曾經參與碳盤查",
    "非常熟悉並可教學"
])

survey_data["q2"] = st.radio("2️⃣ 您使用本系統的主要動機為？", [
    "個人學習 ESG 知識",
    "幫助公司盤查與因應壓力",
    "準備考試或證照",
    "好奇試用"
])

survey_data["q3"] = st.multiselect("3️⃣ 您目前面臨哪些永續壓力？", [
    "政府法規或稽查",
    "客戶或供應鏈要求",
    "內部 ESG 承諾或目標",
    "尚未感受到壓力"
])

survey_data["q4"] = st.radio("4️⃣ 您的角色或身分是？", [
    "老闆 / 負責人",
    "永續專責 / 管理部門",
    "現場部門主管 / 員工",
    "顧問 / 教育人員",
    "學生或自由學習者"
])

survey_data["q5"] = st.radio("5️⃣ 您是否有 ESG 或碳盤查的相關經驗？", [
    "完全沒有",
    "參加過課程但尚未實作",
    "有參與實作經驗",
    "協助完成過 ESG 報告",
])

survey_data["q6"] = st.multiselect("6️⃣ 您最想學習的主題？", [
    "碳盤查基礎概念",
    "產品碳足跡與標示",
    "減碳策略與範疇分類",
    "如何撰寫 ESG 報告",
    "永續採購與循環經濟"
])

survey_data["q7"] = st.radio("7️⃣ 您是否有產品碳足跡的相關需求？", [
    "是，有客戶或通路要求",
    "還沒有，但將來可能需要",
    "沒有，暫不考慮"
])

survey_data["q8"] = st.radio("8️⃣ 您偏好的學習方式是？", [
    "條列清楚、說明概念",
    "實際案例導入",
    "一步一步問答引導",
    "影片或圖解輔助",
])

survey_data["q9"] = st.radio("9️⃣ 您希望系統如何回覆您的提問？", [
    "簡單明瞭（不囉嗦）",
    "像老師引導學生那樣",
    "像顧問給策略建議那樣",
    "依照提問靈活調整"
])

survey_data["q10"] = st.radio("🔟 您希望系統給您怎樣的學習體驗？", [
    "給我清楚答案與摘要就好",
    "用提問方式幫我思考",
    "循序漸進、一步步建立知識",
    "依照我目前程度推薦內容"
])

st.markdown("---")

# 問卷階段選擇
st.markdown("### 🧩 請選擇您要進行的診斷階段：")
stage_choice = st.radio(
    "您希望從哪個階段開始？",
    ["初階問卷（僅含基本題）", "進階問卷（含全部題目）"],
    index=0
)

# 設定 stage 為 "basic" 或 "advanced"
st.session_state.stage = "advanced" if stage_choice == "進階問卷（含全部題目）" else "basic"

    # 直接處理問卷的提交按鈕
submit = st.button("🚀 開始教學")  # 提交按鈕

if submit:
    # 儲存問卷資料
    st.session_state.user_intro_survey = survey_data
    st.session_state.welcome_submitted = True
    st.success("✅ 問卷完成，開始進入 ESG 教學診斷流程")
    st.rerun()  # 重新載入頁面以便進入下一步
