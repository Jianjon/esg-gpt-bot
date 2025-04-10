# src/utils/rag_helper.py

from src.managers.guided_rag import GuidedRAG
from src.utils.gpt_tools import call_gpt

VECTOR_STORE_PATH = "data/vector_store"
rag_engine = GuidedRAG(vector_path=VECTOR_STORE_PATH, model="gpt-4o")

def get_rag_insight(topic: str, question_id: str, question_text: str) -> str:
    try:
        chunks = rag_engine.search_related_chunks(question_text)
        top_chunks = chunks[:2]
        combined_text = "\n\n".join([c["text"] for c in top_chunks])
        return combined_text if combined_text else "（目前查無相關資料）"
    except Exception as e:
        print(f"⚠️ RAG 查詢失敗：{e}")
        return "（查詢補充資料時發生錯誤）"

def generate_user_friendly_prompt(
    current_q: dict,
    user_profile: dict,
    previous_summary: str = "",
    rag_context: str = ""
) -> str:
    # 取得當前問題的基本資料
    question_text = current_q.get("text", "")
    topic = current_q.get("topic", "")
    qid = current_q.get("id", "")
    learning_goal = current_q.get("learning_goal", "")
    
    # 如果沒有提供 RAG，就自動查詢一次
    if not rag_context:
        rag_context = get_rag_insight(topic, qid, question_text)

    # 使用者背景
    role = user_profile.get("q4", "")
    motivation = user_profile.get("q2", "")
    experience = user_profile.get("q5", "")

    # 顧問引導語組合：上下分段
    prompt = f"""
你是一位 ESG 顧問，正在協助使用者進行問卷診斷。

【上一題小結】（上一題回答回顧）：
{previous_summary if previous_summary else "目前尚無小結，請繼續作答！"}

【學習目標與補充資料】：
- 題目內容：{question_text}
- 學習目標：{learning_goal}
- 補充資料：{rag_context}

請根據以上資料，產出一段不超過 150 字的引導語，幫助使用者理解本題要如何作答，語氣親切、鼓勵、具教育性。
"""

    return call_gpt(prompt, temperature=0.5)
