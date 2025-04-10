# src/utils/prompt_builder.py

import json
from src.utils.gpt_tools import call_gpt
from managers.profile_manager import get_user_profile

user_profile = get_user_profile()

TONE_STYLE_MAP = {
    "gentle": "語氣請溫和、鼓勵，就像是一位親切的顧問陪伴企業主學習。",
    "professional": "語氣請專業、邏輯清晰，像在和主管級使用者簡報重點。",
    "creative": "語氣請啟發性、跳脫傳統，鼓勵使用者從不同視角思考。"
}


def build_learning_prompt(question_text: str, learning_goal: str, tone: str) -> str:
    """
    將原始題目與學習目標轉換成口語化顧問引導語 prompt，給 GPT 使用。

    Args:
        question_text (str): 題目原文
        learning_goal (str): 該題的學習目標
        tone (str): 顧問語氣風格（例如：親切鼓勵、溫和專業）

    Returns:
        str: 可丟給 GPT 的提示語 prompt
    """
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    return f"""
你是一位碳盤查顧問，熟悉 ISO 14064-1 標準，正在協助使用者理解一個問題的背景與重點。

請以「{style_instruction}」的語氣，簡單說明以下問題的含義與學習目標，
幫助使用者理解本題要怎麼思考與回答，並且選擇出符合自己公司現狀的選項。

【題目內容】：
{question_text}

【學習目標】：
{learning_goal}

請用不超過 100 字，生成一段口語化引導說明，語氣溫和、具啟發性。
"""


def generate_user_friendly_prompt(
    current_q: dict,
    user_profile: dict,
    previous_summary: str = "",
    rag_context: str = "",
    tone: str = "gentle"
) -> str:
    """
    根據題目與使用者背景，產生自然語氣的顧問式引導語。
    分兩段說明：銜接（上題→本題）、導入（題目重點與學習情境）。
    """
    learning_goal = current_q.get("learning_goal", "")
    topic = current_q.get("topic", "")
    question_note = current_q.get("question_note", "")

    role = user_profile.get("q4", "")
    motivation = user_profile.get("q2", "")
    experience = user_profile.get("q5", "")
    industry = user_profile.get("industry", "某產業")

    TONE_STYLE_MAP = {
        "gentle": "請用溫和親切的語氣，就像一位資深顧問正與企業主面對面交談。",
        "professional": "請用專業簡潔的語氣，強調邏輯與重點。",
        "creative": "請用啟發性語氣，引導使用者從不同視角看待本題。"
    }
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    prompt = f"""
你是一位碳盤查顧問，熟悉 ISO 14064-1 標準，正在協助企業主進行 ESG 問卷的學習與思考。

請根據以下資訊，產出一段具啟發性的自然語氣引導文字，共兩段，每段約 150–180 字：
【段落一：銜接】
請根據「上一題摘要」引導進入本題，用一句自然銜接的方式開始，說明這題與前一題的關聯，幫助使用者建立連貫感。

【段落二：導入】
針對本題「{topic}」，幫使用者點出核心重點與常見情境，引導其思考與回答。可提到「學習目標：{learning_goal}」。

【語氣風格】
{style_instruction}

【本題主題】：{topic}
【學習目標】：{learning_goal}
【題目補充說明】：{question_note or '（無）'}

【使用者背景】
- 行業：{industry}
- 角色：{role}
- 動機：{motivation}
- 經驗：{experience}

【上一題摘要】
{previous_summary or '（第一題:教導用戶依問題去選擇出符合公司的狀況,及系統的使用方法）'}

【知識補充（來自資料庫）】
{rag_context or '（上網找對應的資料）'}

請輸出一段自然語氣的顧問引導語，段落可條列，也可自然敘述，務必讓使用者覺得這段話是針對他設計的。
"""
    from src.utils.gpt_tools import call_gpt
    reply = call_gpt(prompt)
    return reply.strip()



def generate_dynamic_question_block(user_profile: dict, current_q: dict, user_answer: str = "", tone: str = "親切鼓勵") -> str:
    return f"""
你是一位碳盤查顧問，熟悉 ISO 14064-1 標準，正在協助使用者完成一份學習型問卷。

請根據使用者背景、前一題的回答、目前題目的內容與學習目標，
幫我改寫本題的「提問方式」與「說明引導語」。
所設計的題目內容是要讓使用者選擇出最符合自己公司的選項。
說明題目時要讓用戶感到是針對他的背景與需求所設計的內容，「關注企業主背景、貼近實務情境的顧問式提問」。
而不是單純的題目及題目說明。

✏️【格式要求】
1. 題目：15～30 字，精簡口語
2. 說明：50～100 字，具教育性，引導思考

📘【使用者背景】
{json.dumps(user_profile, ensure_ascii=False, indent=2)}

🧾【前一題的回答】
{user_answer if user_answer else "（尚無回覆）"}

📝【原始題目】
{current_q.get("question_text", "")}

📎【原始說明】
{current_q.get("question_note", "")}

🎯【學習目標】
{current_q.get("learning_goal", "")}

請輸出以下格式：
【題目】
（改寫後題目）

【說明】
（口語化說明）

"""

def generate_option_notes(current_q: dict, tone: str = "說明清楚"):
    return f"""
你是一位碳盤查顧問，熟悉 ISO 14064-1 標準，正在補充一題問卷的選項說明。

以下是這題的選項：

{chr(10).join([f"{opt}. {val}" for opt, val in zip(['A', 'B', 'C', 'D', 'E'], current_q.get('options', []))])}

請為每個選項補充一句「10～25 字」的說明，語氣自然、簡潔。

輸出格式：
A. 少於50人 —— 小型規模，碳盤查較簡單
...
"""
