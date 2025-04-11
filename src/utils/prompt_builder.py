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


def build_learning_prompt(
    tone: str = "gentle",
    previous_summary: str = "",
    is_first_question: bool = False,
    user_profile: dict = None
) -> str:
    """
    簡短顧問式引導（第一題為操作說明，其餘題則為前情摘要＋學習目標提示）
    適合放在選項上方，快速協助進入情境。
    """

    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    user_profile = user_profile or {}
    industry = user_profile.get("industry", "某產業")
    profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    if is_first_question:
        prompt = f"""
你是一位 ESG 顧問，正在協助使用者開始一份 ESG 學習型問卷。

請以「{style_instruction}」語氣說明這份問卷的目的與操作方式，
讓使用者放鬆進入狀況。

請參考以下使用者背景：
{profile_json}

✅ 引導重點：
- 告訴這是用來學習與對話的問卷
- 可以選擇、跳過或自填
- 回答的目的是幫助顧問後續提供診斷與建議

請產出一段引導語，最後附上三點提醒（使用條列式，粗體關鍵詞）。
"""
    else:
        prompt = f"""
你是一位 ESG 顧問，正在幫助企業主逐步理解 ESG 問卷的學習邏輯與問題意圖。

請根據「{style_instruction}」語氣，撰寫一段簡潔引導段落，協助使用者銜接上一題總結並了解這題的學習目的。

請參考以下背景與資訊：

🏢【使用者產業】：{industry}
📘【使用者背景】：
{profile_json}

📌【上一題摘要】
{previous_summary or '（無摘要）'}


請產出一段 80～100 字內的顧問式說明，最後加入 2～3 點條列式提示（每列加粗關鍵名詞）。
"""

    from src.utils.gpt_tools import call_gpt
    return call_gpt(prompt).strip()


def generate_user_friendly_prompt(
    current_q: dict,
    user_profile: dict,
    rag_context: str = "",
    tone: str = "gentle"
) -> str:
    """
    根據學習目標與使用者情境，產出一段自然口語、顧問式的引導語，避免重複題目內容。
    """

    learning_goal = current_q.get("learning_goal", "")
    topic = current_q.get("topic", "")
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    industry = user_profile.get("industry", "某產業")

    TONE_STYLE_MAP = {
        "gentle": "語氣親切自然，像一位熟悉企業場景的顧問，與中小企業主溝通。",
        "professional": "語氣專業簡潔，重點導向，讓使用者快速抓到重點。",
        "creative": "語氣啟發、有畫面感，引導使用者跳脫框架思考。"
    }
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    prompt = f"""
你是一位資深 ESG 顧問，熟悉 ISO 14064-1 標準，正在協助企業主進行 ESG 問卷的學習與思考。

請依據「學習目標」來撰寫一段顧問式引導文字，幫助使用者理解該主題的意義、做法或挑戰。避免重複題目內容，並結合使用者背景情境。

✏️ 回應格式要求：
- 引導語須自然口語、脈絡清楚，讓使用者快速理解本題背景與方向
- 結尾請加入 2～3 項條列提示，每項須加上 **粗體關鍵名詞**
- 回應風格請符合下列描述：{style_instruction}

🎯【學習目標】
{learning_goal or '（本題尚未提供學習目標）'}

🏢【使用者背景】
行業：{industry}
問卷回覆摘要如下：
{user_profile_json}

📚【補充資料（選填）】
{rag_context or '（如無補充）'}

請生成一段貼近使用者、聚焦學習目標的專業引導語，結尾加入重點提示。
"""

    from src.utils.gpt_tools import call_gpt
    return call_gpt(prompt).strip()


def generate_dynamic_question_block(user_profile: dict, current_q: dict, user_answer: str = "", tone: str = "gentle") -> str:
    tone_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    question_text = current_q.get("question_text", "")
    question_note = current_q.get("question_note", "")
    learning_goal = current_q.get("learning_goal", "")

    return f"""
你是一位碳盤查顧問，熟悉 ISO 14064-1 標準，正在協助使用者完成一份學習型問卷。

請根據使用者背景、前一題的回答、目前題目的內容與學習目標，
幫我改寫本題的「提問方式」與「說明引導語」。
所設計的題目內容是要讓使用者選擇出最符合自己公司的選項。
說明題目時要讓用戶感到是針對他的背景與需求所設計的內容，
而不是單純的題目及題目說明。

⚠️ 請不要直接使用原始題目或說明中的句子，請改寫成貼近企業場景的提問與說明。
語氣自然、口語化，像是與企業主對話。
【語氣風格】
{tone_instruction}

✏️【格式要求】
1. 題目：15～30 字，精簡口語
2. 說明：50～100 字，具教育性，引導思考

📘【使用者背景】
{json.dumps(user_profile, ensure_ascii=False, indent=2)}

🧾【前一題的回答】
{user_answer if user_answer else "（尚無回覆）"}

📝【題目內容與說明（僅供參考）】
【題目】{question_text}
【說明】{question_note}

🎯【學習目標】
{learning_goal}

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
