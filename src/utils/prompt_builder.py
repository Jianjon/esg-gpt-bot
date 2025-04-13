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
    根據學習目標與使用者角色與情境，產出一段自然口語、顧問式的引導語。
    """
    import json
    from src.utils.gpt_tools import call_gpt

    learning_goal = current_q.get("learning_goal", "")
    topic = current_q.get("topic", "")
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")

    TONE_STYLE_MAP = {
        "gentle": "語氣親切自然，像一位熟悉企業場景的顧問，與中小企業主溝通。",
        "professional": "語氣專業簡潔，重點導向，讓使用者快速抓到重點。",
        "creative": "語氣啟發、有畫面感，引導使用者跳脫框架思考。"
    }
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    prompt = f"""
你是一位資深 ESG 顧問，熟悉 ISO 14064-1 標準，正在協助企業進行 ESG 問卷引導。

請依據「學習目標」，結合使用者背景與角色，撰寫一段引導式說明，協助使用者理解本題的核心概念與挑戰。

🎯【目的】
- 幫助使用者理解：{topic}這一題在問什麼？為什麼重要？
- 引導使用者思考如何針對自己公司來作答
- 語氣應該自然像對話，**整合說明與提問**為一段口語敘述


🧑‍💼【使用者角色】：{role}
請根據這個角色調整語氣與內容,但要維持專業性,口氣要自然,不要太生硬。 但不要使用「你」或「妳」這種稱呼，保持中立。也不需要一直打招呼。
- 若是「企業主」，請從決策與經營角度說明意義與風險
- 若是「永續專責人員」，請著重在執行流程與可行做法
- 若是「行政或財務人員」，請強調配合責任與資料來源
- 若無法辨識角色，請以中性實務方式說明. 不能直接稱呼使用者或是叫老闆及職稱,要維持專業性度口氣自然,不要太生硬。
- 不要使用「請」或「謝謝」這種客套語氣，保持專業性度口氣自然,不要太生硬。
- 不需要一直打招呼。


🧠【格式建議】請根據內容靈活選擇適合的呈現方式：
- 若為比較型、條件型、對應邏輯 → 可使用表格呈現
- 若為清單、操作步驟、注意事項 → 請使用條列清單
- 若為說明性內容 → 請使用 1～2 段自然語句解釋背景與建議
- 若有需要，也可在適當位置加入表情符號（如 ✅、📌、📝）輔助視覺導引

⚠️ 不要強制使用格式，請自行判斷哪種結構最利於閱讀與理解
，每項加上 **粗體關鍵詞**
- 回應風格請符合下列描述：{style_instruction}

🎯【學習目標】
{learning_goal or '（本題尚未提供學習目標）'}

🏢【使用者背景】
行業：{industry}
完整資料如下：
{user_profile_json}

📚【補充資料（選填）】
{rag_context or '（如無補充）'}

📏【長度建議】
- 本段回應請控制在 **180～250 字**，足夠清楚教學但不宜過長。
- 可使用條列或表格輔助視覺，但不需撐長篇幅。

請聚焦於該題的「學習目標」進行引導說明，幫助使用者了解該主題的實務意義與回答方向。結尾加入條列提示。
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
    tone_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    question_text = current_q.get("text", "")
    question_note = current_q.get("question_note", "")
    learning_goal = current_q.get("learning_goal", "")
    role = user_profile.get("role", "企業內部人員")
    profile_json = json.dumps(user_profile, ensure_ascii=False)

    prompt = f"""
你是一位資深 ESG 顧問，熟悉中小企業經營情境與碳盤查實務。

請根據以下資訊，撰寫一段約 80～120 字的「顧問式引導語」，幫助使用者了解本題的**選項差異**，並能依據自身情況做出判斷。

🌱 引導語風格：「{tone_instruction}」

🧑‍💼【使用者角色】：{role}
📘【使用者背景】：{profile_json}
📝【題目】：{question_text}
📌【補充說明】：{question_note}
🎯【學習目標】：{learning_goal}
🗣️【前一題作答】：{user_answer or "（無資料）"}

✅【內容要求】
- 不需要一直打招呼。
- 不要只是解釋背景，要點出「不同選項的意義差異」
- 引導使用者思考「自己公司屬於哪一種情境」
- 語氣自然、口語化，像顧問正在和企業老闆聊天
- 回應中請加入 **至少 2 個黑體關鍵詞**
- 不要出現任何「提示語」或「格式說明」
- 不要使用「你」或「妳」這種稱呼，保持中立。
- 不要使用「請」或「謝謝」這種客套語氣，保持專業性度口氣自然,不要太生硬。

📤 請直接輸出這段引導語。
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
