# rag_helper.py
from vector_builder.vector_store import VectorStore
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

# ✅ 新增：用向量庫搜尋與自動補上下文
vs = VectorStore()
vs.load("data/vector_output_hf/ISO 14064-1")  # 📁 可改為對應主題的資料夾

def generate_rag_based_prompt(
    current_q: dict,
    user_profile: dict,
    previous_summary: str = "",
    rag_context: str = ""
) -> str:
    question_text = current_q.get("text", "")
    learning_goal = current_q.get("learning_goal", "")
    tone = "溫和鼓勵"

    # ✅ 自動查詢相關段落（若未傳入 rag_context）
    if not rag_context:
        results = vs.search(question_text, top_k=4)
        rag_context = "\n\n".join([r["text"] for r in results])

    # ✅ 串接 Prompt
    prompt = f"""
你是一位專業的永續顧問，正在協助企業進行 ESG 問卷診斷。
請使用 {tone} 的語氣，根據以下資訊協助解釋問題重點，引導使用者理解與作答：

【使用者背景】
{user_profile}

【學習目標】
{learning_goal}

【問題內容】
{question_text}

【相關段落資料】
{rag_context}

請用條列方式引導思考，最後鼓勵使用者依照理解自行作答。
"""
    return prompt
