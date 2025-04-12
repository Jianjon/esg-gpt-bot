# src/utils/report_utils.py

def generate_user_background_section(user_intro_data: dict) -> str:
    """
    根據使用者前導問卷資料，產出報告中「使用者背景說明」段落。
    """
    lines = []
    for key, value in user_intro_data.items():
        lines.append(f"- {key}：{value}")
    return "### 👤 使用者背景摘要\n" + "\n".join(lines)
