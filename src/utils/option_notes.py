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

請回傳 **純 JSON 格式**，不要加上 ```json 或任何說明：

{{
  "選項A": "補充說明",
  "選項B": "補充說明"
}}

✅ 只輸出 JSON 結果。
"""

    response = call_gpt(prompt)

    # 處理 GPT 回傳（移除開頭或 code block 符號）
    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response.lstrip("```json").rstrip("```").strip()
        elif response.startswith("```"):
            response = response.lstrip("```").rstrip("```").strip()

        return json.loads(response)
    except Exception as e:
        print(f"⚠️ GPT 回傳解析失敗：{e}\n原始回應：{response}")
        return {opt: "" for opt in options}
