from openai import OpenAI
from typing import List, Dict
import streamlit as st
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

# --- 對話紀錄（每一題對應一個對話 thread） ---
# ✅ 初始化必要欄位
if "qa_threads" not in st.session_state:
    st.session_state.qa_threads = {}

if "context_history" not in st.session_state:
    st.session_state.context_history = []

if "guided_chat" not in st.session_state:
    st.session_state.guided_chat = []

if "guided_turns" not in st.session_state:
    st.session_state.guided_turns = 0

def get_conversation(question_id: str) -> List[Dict[str, str]]:
    return st.session_state.qa_threads.get(question_id, [])

def add_turn(question_id: str, user_input: str, assistant_reply: str):
    if question_id not in st.session_state.qa_threads:
        st.session_state.qa_threads[question_id] = []
    st.session_state.qa_threads[question_id].append({
        "user": user_input,
        "assistant": assistant_reply
    })
def generate_following_action(question_id: str) -> str:
    """
    根據某一題的所有對話紀錄，自動總結一段後續建議（following action）
    """
    history = st.session_state.qa_threads.get(question_id, [])
    if not history:
        return "（尚無足夠對話內容）"

    # 整理所有提問與回覆
    chat_log = "\n".join(
        [f"使用者：{turn['user']}\nAI：{turn['assistant']}" for turn in history]
    )

    prompt = f"""
請根據以下使用者與 AI 關於 ESG 題目的對話，生成一段具體的「後續行動建議」，限 2–3 句話，明確指出下一步可執行的改善方向。

對話紀錄：
{chat_log}

請以「建議：」開頭，輸出具體可行的建議：
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位幫助企業進行 ESG 分析與診斷的顧問助理。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=120
        )
        result = response["choices"][0]["message"]["content"].strip()
        return result

    except Exception as e:
        print("⚠️ following action 產生失敗：", e)
        return "（GPT 產生建議失敗）"
