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
    題目前導論提示（第一題為操作引導，其餘為總結上題與學習目標說明），
    可根據使用者角色調整語氣與內容，幫助他理解題目設計邏輯與參與方式。
    """

    from src.utils.gpt_tools import call_gpt
    import json

    style_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    user_profile = user_profile or {}
    industry = user_profile.get("industry", "某產業")
    role = user_profile.get("role", "企業內部人員")
    profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    if is_first_question:
        prompt = f"""
    你是一位資深 ESG 顧問，正在逐題協助企業使用者理解 ESG 問卷設計的學習邏輯與實務意涵。
    請根據下列背景資訊，{style_instruction}

    🧑‍💼【使用者角色】：{role}
    請根據角色調整說明角度：
    - 若是「企業主」，請說明此問卷將幫助他理解風險、因應法規與市場
    - 若是「永續專責人員」，請強調如何執行這些流程、未來如何應用結果
    - 若是「行政或財務人員」，請強調如何協助資料收集與配合工作

    📝【使用者背景】
    {profile_json}

    🎯【學習導論要求】
    請從以下三個方向切入說明，引導使用者進入 ESG 學習流程：
    1. **碳盤查的基礎概念**：說明何謂碳盤查、目的與重要性。
    2. **碳盤查對企業的影響**：說明這與營運、法規、風險管理的關係。
    3. **碳盤查的執行步驟**：讓使用者知道這不是填問卷，而是一連串流程。

    ✅ 回應格式要求：
    🧠【格式建議】請根據內容靈活選擇適合的呈現方式：
    - 若為比較型、條件型、對應邏輯 → 可使用表格呈現
    - 若為清單、操作步驟、注意事項 → 請使用條列清單（每列加上 **粗體重點**）
    - 若為說明性內容 → 請使用 1～2 段自然語句解釋背景與建議
    - 若有需要，也可在適當位置加入表情符號（如 ✅、📌、📝）輔助視覺導引

    ⚠️ 不要強制使用格式，請自行判斷哪種結構最利於閱讀與理解。
    請直接產出這段「引導開場說明」，不要有標題，不要補充說明。
    """

    else:
        prompt = f"""
你是一位 ESG 顧問，正在逐題協助使用者理解 ESG 問卷的設計邏輯與學習目的。

這題為第二題起，請你根據「上一題摘要 + 本題目標 + 使用者角色」，給出一段自然的導論說明，引導使用者投入思考。

🧑‍💼【使用者角色】：{role}
請根據角色調整語氣與內容：
- 「企業主」→ 決策邏輯與實務意義
- 「永續專責人員」→ 執行方法與應用情境
- 「行政或財務人員」→ 配合責任與資料位置

🏢【產業】：{industry}
📘【使用者背景】：
{profile_json}

📌【上一題摘要】
{previous_summary or '（尚無摘要）'}

✅ 回應格式要求：
🧠【格式建議】請根據內容靈活選擇適合的呈現方式：
- 若為比較型、條件型、對應邏輯 → 可使用表格呈現
- 若為清單、操作步驟、注意事項 → 請使用條列清單（每列加上 **粗體重點**）
- 若為說明性內容 → 請使用 1～2 段自然語句解釋背景與建議
- 若有需要，也可在適當位置加入表情符號（如 ✅、📌、📝）輔助視覺導引

⚠️ 不要強制使用格式，請自行判斷哪種結構最利於閱讀與理解
請直接產出這段「引導開場說明」，不要有標題，不要補充說明。
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
請根據這個角色調整語氣與內容：
- 若是「企業主」，請從決策與經營角度說明意義與風險
- 若是「永續專責人員」，請著重在執行流程與可行做法
- 若是「行政或財務人員」，請強調配合責任與資料來源
- 若無法辨識角色，請以中性實務方式說明

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

def generate_dynamic_question_block(
    user_profile: dict,
    current_q: dict,
    user_answer: str = "",
    tone: str = "gentle"
) -> str:
    import json
    from src.utils.gpt_tools import call_gpt

    tone_instruction = TONE_STYLE_MAP.get(tone, TONE_STYLE_MAP["gentle"])
    question_text = current_q.get("question_text", "")
    question_note = current_q.get("question_note", "")
    learning_goal = current_q.get("learning_goal", "")
    role = user_profile.get("role", "企業內部人員")
    profile_json = json.dumps(user_profile, ensure_ascii=False)

    prompt = f"""
你是一位資深 ESG 顧問，正在協助「{role}」完成 ESG 問卷。

請根據以下資訊，產生一段 **不超過 120 字** 的引導句，用自然、顧問式的語氣，幫助使用者理解這題的意義，並思考自己公司會如何回答。

--- 
📝【題目】：{question_text}
📘【補充說明】：{question_note}
👤【用戶背景】：{profile_json}

--- 

✅【格式要求】：
- 字數請控制在 60～120 字
- 口吻自然、情境化，像在和企業主說話
- 加入至少 2 個**黑體關鍵詞**
- 請輸出一段「完整、整合式的句子」，不要分段、不要出現任何標題或多餘格式

📤 請直接輸出這段引導語即可。
    """

    return call_gpt(prompt).strip()


def generate_option_notes(current_q: dict, tone: str = "說明清楚") -> str:
    options = current_q.get('options', [])
    option_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])

    prompt = f"""
你是一位資深碳盤查顧問，熟悉 ISO 14064-1 與企業永續實務。

以下是 ESG 問卷中一題的選項內容，請針對每一項補充一句「**簡短清楚的說明（10～25 字內）**」，幫助使用者快速理解。

--- 
📋【選項原文】：
{option_text}

--- 
✅【撰寫要求】：
- 每個選項對應一句話說明
- 請以**親切、明確**語氣撰寫
- 不用加編號，只輸出說明句
- 避免術語，讓一般企業主也能看懂
- 若為規模選項，可描述其在 ESG 上的「特性」或「處理難易度」

📝 請依序列出 A~E 五個說明（若有），例如：
- 小型規模，碳盤查作業最簡單
- 多據點管理，需整合數據彙整...

請直接開始，不要加多餘說明。
    """
    return prompt.strip()
