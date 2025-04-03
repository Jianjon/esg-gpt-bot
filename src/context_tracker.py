from openai import OpenAI
from typing import List, Dict
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化記憶結構
if "context_history" not in st.session_state:
    st.session_state.context_history = []

def add_context_entry(question_id: str, user_response, question_text: str):
    """
    將使用者的回答與對應問題送進 GPT，生成簡短摘要並儲存
    """
    answer_text = ", ".join(user_response) if isinstance(user_response, list) else str(user_response)

    prompt = f"請用一兩句話總結以下 ESG 問題與回答的重點，用於顧問回顧使用：\n\n問題：{question_text}\n回答：{answer_text}\n\n摘要："

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

        st.session_state.context_history.append({
            "id": question_id,
            "answer": answer_text,
            "summary": summary
        })
        return summary

    except Exception as e:
        print(f"⚠️ GPT 摘要失敗：{e}")
        return "（摘要失敗）"

def get_all_summaries() -> List[str]:
    return [f"Q{entry['id']}：{entry['summary']}" for entry in st.session_state.context_history]
