# src/utils/prompt_builder.py

import json
from src.utils.gpt_tools import call_gpt
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

TONE_STYLE_MAP = {
    "gentle": "語氣請溫和、鼓勵，就像是一位親切的顧問陪伴企業主學習。",
    "professional": "語氣請專業、邏輯清晰，像在和主管級使用者簡報重點。",
    "creative": "語氣請啟發性、跳脫傳統，鼓勵使用者從不同視角思考。"
}

def build_learning_prompt(
    user_profile: dict,
    current_q: dict,
    previous_summary: str,
    tone: str = "gentle"
) -> str:
    """
    第二題以後專用：根據「上一題摘要 + 使用者角色 + 本題內容」，產出導論小結說明。
    """
    from src.utils.gpt_tools import call_gpt
    import json

    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")
    profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位 ESG 顧問，正在逐題引導企業用戶{style_instruction}完成 ESG 問卷學習。

本題為第二題之後，請根據「上一題摘要」，提供一段導論說明，幫助使用者回顧前題重點並自然進入新問題的思考,及建議的管理作法。

🧑‍💼【使用者角色】：{role}
🏭【產業類別】：{industry}
📘【使用者背景】：
{profile_json}

📌【上一題摘要】：
{previous_summary or '（尚無摘要）'}


✅【撰寫指引】：
- 以一段自然語句，先回顧上題重點，再銜接說明本題重點
- 可使用條列、分段或語句說明，保持親切、具邏輯感
- 適當使用表情符號（📌、✅、📝）輔助強調


⚠️ 不需要加入任何標題或提示，請直接開始輸出顧問式說明。
"""
    return call_gpt(prompt).strip()


def build_intro_welcome_prompt(
    user_profile: dict,
    current_q: dict,
    tone: str = "gentle"
) -> str:
    """
    專用於第一題的開場歡迎與導入語。
    根據使用者背景與學習動機產出友善說明，引導進入學習。
    """
    from src.utils.gpt_tools import call_gpt
    import json

    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "一般成員")
    motivation = user_profile.get("q2", "")
    profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位 ESG 顧問，現在正協助企業使用者進入 ESG 學習問卷的第一題。

請針對以下資訊{style_instruction}，產出一段親切、具鼓勵性的開場說明，讓使用者理解這份問卷的目的與參與價值：

🧑‍💼【使用者角色】：{role}
🏭【產業類別】：{industry}
🎯【學習動機】：{motivation}
📘【背景摘要】：
{profile_json}

📝【引導目標】：
- 為何這份問卷對企業主/員工/管理層有幫助？
- 如何協助他理解 ESG / 碳盤查概念？
- 預告問卷會怎麼進行，讓人有安全感

🧠【格式建議】請根據內容靈活選擇適合的呈現方式：
- 若為比較型、條件型、對應邏輯 → 可使用表格呈現
- 若為清單、操作步驟、注意事項 → 請使用條列清單
- 回應文字請控制在 ChatGPT 風格的內文範圍（約 16px 顯示大小）
✅ 請產出約 150 字自然說明語句。
回應只產出文字內容，不要加上標題或其他說明。不能直接稱呼使用者或是叫老闆及職稱.使用中性實務方式說明。
- 不要使用「你」或「妳」這種稱呼，保持中立。
    """

    return call_gpt(prompt).strip()



def generate_user_friendly_prompt(
    current_q: dict,
    user_profile: dict,
    rag_context: str = "",
    tone: str = "gentle"
) -> str:
    """
    教科書式風格的導讀語生成器：清楚、結構統一、不打招呼、無廢話。
    """
    import json
    from src.utils.gpt_tools import call_gpt

    learning_goal = current_q.get("learning_goal", "")
    topic = current_q.get("topic", "")
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")

    # 對應語氣風格（tone）做微調說明，仍以實務導向為主
    TONE_STYLE_MAP = {
        "gentle": "語氣自然清晰，像教科書內的小節導讀，內容有邏輯、有層次。",
        "professional": "語氣簡潔精準，重點導向，避免贅字與情緒詞彙。",
        "creative": "語氣帶引導與畫面感，鼓勵使用者從場景中思考。"
    }
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    # GPT prompt 設計
    prompt = f"""
你是一位資深 ESG 顧問，正在撰寫教學導讀。以下是本題內容、使用者背景與補充資料，請產出一段「教科書式導讀語」，格式統一、語氣專業自然，並依角色客製化重點說明。

【任務格式】
請用下列結構撰寫回應：

【主題概述】
一段 40–60 字簡要說明該題目的核心概念或背景。

【角色導向說明】
根據使用者角色，說明其應特別注意的面向，控制在 2–3 句內。

【思考建議】
以條列式列出 2–3 點評估、資料準備、或判斷方向，便於使用者作答。

【風格限制】
- 不使用稱謂（如您、你、企業主等），保持知識型中性語氣
- 不打招呼、不寒暄、不客套
- 語句清楚有層次，可搭配表情符號（如 ✅ 📌）協助視覺導引
- 每項加入 **粗體關鍵詞**
- 全文 180～250 字以內
- 不使用 GPT 回應框格式，不需補充說明，不要輸出 JSON，只產出內容
- 回應文字請控制在 ChatGPT 風格的內文範圍（約 16px 顯示大小）
【格式提示】
- **粗體** 用於強調重點
- 「」用於技術術語、專有詞
- （）用於輔助說明或判斷條件
- 若需對比或條件選擇，可使用簡單 Markdown 表格呈現
- 若需視覺區分，可使用反白樣式（會自動套用背景色）
- 若需條列式說明，請使用「-」開頭的清單格式
- 若需引用或參考資料，請使用「>」開頭的引用格式

【學習目標】
{learning_goal or '（本題尚未提供學習目標）'}

【使用者角色】
{role}

【行業】
{industry}

【使用者完整資料】
{user_profile_json}

【補充資料】
{rag_context or '（無）'}

【語氣風格】
{style_instruction}

請依以上格式撰寫內容。
    """

    return call_gpt(prompt).strip()


from src.utils.gpt_tools import call_gpt
import json

TONE_STYLE_MAP = {
    "gentle": "語氣請溫和、鼓勵，就像是一位親切的顧問陪伴企業主學習。",
    "professional": "語氣請專業、邏輯清晰，像在和主管級使用者簡報重點。",
    "creative": "語氣請啟發性、跳脫傳統，鼓勵使用者從不同視角思考。"
}
def generate_dynamic_question_block(
    user_profile: dict,
    current_q: dict,
    user_answer: str = "",
    tone: str = "gentle"
) -> str:
    import json
    from src.utils.gpt_tools import call_gpt

    question_text = current_q.get("text", "")
    question_note = current_q.get("question_note", "")
    learning_goal = current_q.get("learning_goal", "")
    role = user_profile.get("role", "企業內部人員")
    industry = user_profile.get("industry", "某產業")
    profile_json = json.dumps(user_profile, ensure_ascii=False)

    TONE_STYLE_MAP = {
        "gentle": "語氣自然、像顧問陪伴討論，強調情境差異與理解。",
        "professional": "語氣簡潔、邏輯清晰，幫助快速判斷選項差異。",
        "creative": "語氣具畫面感、引導發現潛在風險與機會。"
    }
    tone_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    prompt = f"""
你是一位 ESG 顧問，擅長撰寫針對中小企業的問題導引說明。以下是某一題的題目背景與使用者資料，請撰寫一段 80～120 字的「問題引導語」，強調選項的差異性、常見的誤解或風險，幫助使用者理解自己該怎麼判斷選項。

【角色】：{role}
【產業】：{industry}
【使用者完整背景】：
{profile_json}

【題目】：
{question_text}

【補充說明】：
{question_note}

【學習目標】：
{learning_goal}

【語氣風格】：{tone_instruction}

【寫作格式要求】
- ❌ 不打招呼、不客套、不稱呼使用者
- ✅ 直入主題，用一段說明＋條列的方式說明該題的選項差異與判斷重點
- ✅ 至少使用 2 個 **黑體關鍵詞**
- ✅ 可搭配表情符號（如 ✅ 📌）輔助視覺，但不要過多
- ✅ 結尾以一句總結，提示選項選擇要考量什麼條件
- ✅ 請直接輸出文字內容，不需說明格式、不需 JSON、不需外框- 回應文字請控制在 ChatGPT 風格的內文範圍（約 16px 顯示大小）

📤 請根據上方內容直接撰寫一段「針對該題的顧問式提問引導語」。
    """

    return call_gpt(prompt).strip()


def generate_option_notes(current_q: dict, user_profile: dict = {}, tone: str = "gentle") -> dict:
    """
    根據題目選項與使用者背景，請 GPT 幫每個選項補充一段簡短清楚的說明。
    回傳 dict 格式，例如：{"1-10人": "這是說明", ...}
    """
    options = current_q.get('options', [])
    question_text = current_q.get('text', '')
    option_text = "\n".join([f"- {opt}" for opt in options])  # ✅ 不要用 A. B. C. 編號

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
- 回應文字請控制在 ChatGPT 風格的內文範圍（約 16px 顯示大小）

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
