import os
import json
import openai
import streamlit as st
from typing import List, Dict
from src.managers.profile_manager import get_user_profile
from src.utils.gpt_tools import call_gpt
from src.utils.topic_to_rag_map import get_rag_doc_for_question  # ✅ 自動選擇向量庫

# 初始化 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# 取得使用者設定檔
user_profile = get_user_profile()

# 初始化記憶結構
if "context_history" not in st.session_state:
    st.session_state["context_history"] = []
if "qa_threads" not in st.session_state:
    st.session_state["qa_threads"] = {}
if "guided_chat" not in st.session_state:
    st.session_state["guided_chat"] = []
if "guided_turns" not in st.session_state:
    st.session_state["guided_turns"] = 0


# --- 每題摘要紀錄（for 顧問用） ---
def add_context_entry(question_id: str, user_response, question_text: str):
    answer_text = ", ".join(user_response) if isinstance(user_response, list) else str(user_response)

    prompt = f"""請用80-120總結以下 ESG 問題與回答的重點，用於顧問回顧使用：

問題：{question_text}
回答：{answer_text}

摘要："""

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位協助企業診斷 ESG 狀況的顧問助理，擅長快速摘要使用者回覆。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        summary = completion["choices"][0]["message"]["content"].strip()

        # 先移除舊的同題紀錄
        st.session_state["context_history"] = [
            item for item in st.session_state["context_history"]
            if item["id"] != question_id
        ]

        # 加入新摘要
        st.session_state["context_history"].append({
            "id": question_id,
            "answer": answer_text,
            "summary": summary
        })

        return summary

    except Exception as e:
        print(f"⚠️ GPT 摘要失敗：{e}")
        return "（摘要失敗）"


def get_all_summaries() -> List[str]:
    """從 `qa_threads` 中獲取所有問題的摘要（最後一輪回答）。"""
    return [
        f"Q{q_id}：{st.session_state.qa_threads[q_id][-1]['assistant']}"
        for q_id in st.session_state.qa_threads
    ]


# --- 對話紀錄管理 ---
def get_conversation(question_id: str) -> List[Dict[str, str]]:
    return st.session_state.qa_threads.get(question_id, [])

def add_turn(question_id: str, user_input: str, assistant_reply: str):
    if question_id not in st.session_state.qa_threads:
        st.session_state.qa_threads[question_id] = []
    st.session_state.qa_threads[question_id].append({
        "user": user_input,
        "assistant": assistant_reply
    })


# --- 自動產生後續建議（進階版） ---
def generate_following_action(current_q: dict, user_answer: str = "", user_profile: dict = None) -> str:
    import os
    import json
    from src.utils.gpt_tools import call_gpt
    from src.utils.topic_to_rag_map import get_rag_doc_for_question

    question_text = current_q.get("text", "")
    topic = current_q.get("topic", "")
    learning_goal = current_q.get("learning_goal", "")
    user_profile_json = json.dumps(user_profile or {}, ensure_ascii=False, indent=2)

    # ✅ 嘗試取得 rag_doc，並檢查向量資料夾是否存在
    try:
        rag_doc = get_rag_doc_for_question(current_q)
        rag_path = os.path.join("data", "vector_output_hf", rag_doc)
        if not os.path.exists(rag_path):
            print(f"⚠️ 找不到向量資料夾：{rag_path}，略過 RAG。")
            rag_doc = None
    except Exception as e:
        print(f"⚠️ 無法取得向量資料夾（RAG 略過）：{e}")
        rag_doc = None

    prompt = f"""
你是一位 ESG 顧問，熟悉中小企業常見營運情境與合規挑戰。請根據以下資訊，產出「3 條具體可執行的下一步行動建議」。字數控制在 160 字內。

【目標】
- 建議必須能真正執行，不得空泛
- 聚焦實際行動：可以建立什麼制度、找誰合作、做哪種準備
- 每條建議獨立成句，簡潔有力，不補充說明、不包裝語氣

【語氣風格】
- 請模仿 GPT 與使用者的對話語氣
- **語氣溫和但務實**，可以加入「這樣能幫助⋯」「這樣做可以確保⋯」等解釋
- 可搭配 **粗體關鍵詞** 或 emoji 做視覺強調

【排版要求】
- 請將建議分為 3 段，每一段以 emoji（✅ 📌 🔧 等）開頭
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

【使用者背景】
{user_profile_json}

【題目內容】
{question_text}

【學習目標】
{learning_goal}

【使用者回覆】
{user_answer or '（尚未填寫）'}

請產出專業建議（3 條），語氣中性、不空談、不客套。
    """

    try:
        from src.utils.gpt_tools import call_gpt
        reply = call_gpt(prompt=prompt, rag_doc=rag_doc)
        return reply.strip()
    except Exception as e:
        print(f"⚠️ GPT 呼叫失敗：{e}")
        return "⚠️ 無法產生建議，請稍後再試。"
