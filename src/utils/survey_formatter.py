def format_survey_context(survey_data: dict) -> str:
    """
    將使用者填寫的前導問卷資料轉換成清楚的 GPT Prompt 上下文格式。
    """
    if not survey_data:
        return "尚未提供前導問卷資料。"

    # 取出問卷階段
    stage = survey_data.get("selected_stage", "未指定")

    # 題號對應標題（q1 ~ q10）
    question_titles = {
        "q1": "對溫室氣體盤查的認知",
        "q2": "使用本系統的主要動機",
        "q3": "公司目前的永續壓力",
        "q4": "使用者的角色或身分",
        "q5": "過去的 ESG 或碳盤查經驗",
        "q6": "想學習的主題",
        "q7": "是否有產品碳足跡相關需求",
        "q8": "希望的學習方式",
        "q9": "偏好的回答風格",
        "q10": "希望獲得的學習引導"
    }

    context_lines = []
    context_lines.append(f"使用者選擇的診斷階段為：**{stage}**。")

    for key, title in question_titles.items():
        if key in survey_data:
            answer = survey_data[key]
            context_lines.append(f"- {title}：{answer}")

    return "\n".join(context_lines)
