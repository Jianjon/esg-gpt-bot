# src/utils/prompt_builder.py

import json
from src.utils.gpt_tools import call_gpt
from src.managers.profile_manager import get_user_profile
from src.utils.rag_retriever import get_rag_context_for_question

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


def build_intro_welcome_prompt(user_profile: dict, current_q: dict, tone: str = "gentle") -> str:
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
- 回應文字請控制在 ChatGPT 風格的內文範圍,約 16px 顯示大小, 標題字為 18px

✅ 請產出約 150 字自然說明語句。
- 回應只產出文字內容，不要加上標題或其他說明。
- 不可使用「你」「妳」或「企業主」等稱謂，保持中性實務風格。
"""
    return call_gpt(prompt).strip()

def build_learning_prompt(user_profile: dict, current_q: dict, previous_summary: str, tone: str = "gentle") -> str:
    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")
    profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位 ESG 顧問，正在逐題引導企業用戶{style_instruction}完成 ESG 問卷學習。

本題為第二題以後，請根據「上一題摘要」，提供一段導論說明，幫助使用者回顧前題重點並自然進入新問題的思考及建議的管理作法。

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
- 請控制在 120–180 字之間，不需標題或額外框線
"""
    return call_gpt(prompt).strip()

def generate_user_friendly_prompt(current_q: dict, user_profile: dict, rag_context: str = "", tone: str = "gentle") -> str:
    learning_goal = current_q.get("learning_goal", "")
    topic = current_q.get("topic", "")
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")

    if not rag_context:
        try:
            rag_context = get_rag_context_for_question(current_q)
        except Exception as e:
            print(f"⚠️ 無法取得補充資料：{e}")
            rag_context = ""

    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])

    prompt = f"""
你是一位資深 ESG 顧問，正在撰寫教學導讀。以下是本題內容、使用者背景與補充資料，請產出一段「教科書式導讀語」，格式統一、語氣專業自然，並依角色客製化重點說明。

【任務格式】
請用下列結構撰寫回應：標題字不要太大，建議 16px

【主題概述】
一段 80-100 字簡要說明該題目的核心概念或背景。說明該題目對於使用者角色的意義或影響。
根據使用者角色，說明其應特別注意的面向，控制在 2–3 句內。

【思考建議】  
以條列式列出 3–5 點評估、資料準備、或判斷方向，便於使用者作答。

【目標】
- 建議必須能真正執行，不得空泛
- 聚焦實際行動：可以建立什麼制度、找誰合作、做哪種準備
- 每條建議獨立成句，簡潔有力，不補充說明、不包裝語氣

【語氣風格】
- 請模仿 GPT 與使用者的對話語氣
- **語氣溫和但務實**，可以加入「這樣能幫助⋯」「這樣做可以確保⋯」等解釋,不用鼓勵性語氣
- 可搭配 **粗體關鍵詞** 或 emoji 做視覺強調

【排版要求】
- 請將建議分為 3~5 段，每一段以 emoji（✅ 📌 🔧 等）開頭
- 每段落**不超過兩行**，中間可適度換行，保持 GPT 對話風格的節奏
- 每段都應包含一個「明確行動」+「這樣做的原因」
- 保持留白與可讀性，避免密密麻麻,排版要好看,不能太密集
- 條列式時試得要斷行，不能太長

【格式提示】
- **粗體** 用於強調重點
- 「」用於技術術語、專有詞
- （）用於輔助說明或判斷條件
- 若需條列式說明，請使用「-」開頭的清單格式
- 若需引用或參考資料，請使用「>」開頭的引用格式
- 回應文字請控制在 ChatGPT 風格的內文範圍（約 16px 顯示大小）
- 不要使用「你」「妳」或「企業主」等稱謂，保持中性實務風格
- 不要使用「請」或「建議」等語氣，保持中性實務風格  

【學習目標】<-"超級重要"-要聚焦在這個學習目標,不需要重複題目內容,不要發散或是偏題,或講得太廣泛
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

def generate_dynamic_question_block(user_profile: dict, current_q: dict, user_answer: str = "", tone: str = "gentle") -> str:
    question_text = current_q.get("text", "")
    question_note = current_q.get("question_note", "")
    learning_goal = current_q.get("learning_goal", "")
    role = user_profile.get("role", "企業內部人員")
    industry = user_profile.get("industry", "某產業")
    profile_json = json.dumps(user_profile, ensure_ascii=False)
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
- ❌ 不需要標題或提示語，直接開始撰寫
- ✅ 以自然語句引導使用者思考，強調選項差異或誤解
- ✅ 可使用條列式或"分段說明"，保持親切、具邏輯感
- ✅ 每段不超過 3 行，總字數控制在 80–120 字之間,排版要好看,不能太密集
- 條列式時試得要斷行，不能太長

【目標】
- 引導使用者理解「該如何判斷選項」
- 不需解釋每個選項（選項補充會另外顯示）
- 避免密密麻麻，請用 2～3 段落，每段不超過 3 行

【語氣風格】
- 口吻親切自然，但不誇張、不自問自答
- 像 GPT 向用戶簡單說明問題焦點的方式

【排版格式】
- 首段為「題目的意義」或「常見思考盲點」
- 第二段用 ✅ 或 📌 引導條列，可列出 1～2 點判斷方向
- 最後一行總結：提醒使用者依據自身情境思考
- 不要使用「你」「妳」或「企業主」等稱謂，保持中性實務風格
- 不要使用「請」或「建議」等語氣，保持中性實務風格

📤 請根據上方內容直接撰寫一段「針對該題的顧問式提問引導語」。
"""
    return call_gpt(prompt).strip()

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
  "選項1": "補充說明",
  "選項2": "補充說明"
}}

✅ 請直接輸出 JSON 結果，不需要其他說明文字。
"""

    response = call_gpt(prompt)

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