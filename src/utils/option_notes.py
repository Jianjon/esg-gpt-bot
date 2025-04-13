import json
from src.utils.gpt_tools import call_gpt

def generate_option_notes(current_q: dict, user_profile: dict = {}, tone: str = "gentle") -> dict:
    options = current_q.get('options', [])
    question_text = current_q.get('text', '')
    option_text = "\n".join([f"- {opt}" for opt in options])
    profile_hint = json.dumps(user_profile, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位 ESG 顧問，擅長針對題目選項進行簡潔說明。以下是題目內容與使用者背景：

【題目內容】
{question_text}

【選項】
{option_text}

【使用者背景】
{profile_hint}

📌 請根據使用者的「產業」、「角色」與「作答動機」，針對每個選項補充一句 15~25 字的中文說明。
請盡量貼近該產業的實際情境舉例，例如內場管理、供應商合作、人力配置等。
語氣請符合「{tone}」風格，避免使用術語或模糊字詞。

請回傳 JSON 格式如下：

{{
  "1-10人": "說明內容",
  "11-50人": "說明內容",
  ...
}}

✅ 請直接輸出 JSON 結果，不需要補充說明或其他文字。
"""

    response = call_gpt(prompt)

    try:
        return json.loads(response)
    except Exception as e:
        print(f"⚠️ GPT 回傳解析失敗：{e}")
        return {opt: "" for opt in options}
