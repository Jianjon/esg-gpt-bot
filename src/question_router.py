import openai
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def recommend_next_question(summary_history: List[Dict], unanswered_questions: List[Dict]) -> Dict:
    """
    根據目前已回答摘要與剩餘題目，讓 GPT 推薦下一題
    回傳下一題 dict（id, text, topic）
    """
    if not unanswered_questions:
        return {}

    history_text = "\n".join([f"Q{item['id']}：{item['summary']}" for item in summary_history])

    prompt = f"""
你是一位幫助企業完成 ESG 問卷診斷的顧問。
根據以下使用者已完成的題目摘要，請從待完成題目中，挑選一題你認為最適合下一步提問，並只輸出那一題的 ID：

✅ 使用者已完成：
{history_text}

📋 候選題目如下：
{[q['id'] + '：' + q['text'][:30] + '...' for q in unanswered_questions]}

請輸出最推薦的題目 ID（例如：S005）
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位嚴謹且理解 ESG 脈絡的策略顧問。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=20
        )
        result = response["choices"][0]["message"]["content"].strip()
        for q in unanswered_questions:
            if q["id"] == result:
                return q
        return unanswered_questions[0]  # fallback
    except Exception as e:
        print("GPT 問題推薦失敗：", e)
        return unanswered_questions[0]
