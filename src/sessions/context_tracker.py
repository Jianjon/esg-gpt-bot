import os
import json
import openai
import streamlit as st
from typing import List, Dict
from src.managers.profile_manager import get_user_profile
from src.utils.gpt_tools import call_gpt

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
    question_text = current_q.get("text", "")
    topic = current_q.get("topic", "")
    learning_goal = current_q.get("learning_goal", "")
    user_profile_json = json.dumps(user_profile or {}, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位 ESG 顧問，請根據使用者針對下列 ESG 問題的回答內容，產出「下一步行動建議」：

1. 建議內容需具體可行，與該題學習目標和使用者背景相關。
2. 請條列出 3–5 點行動建議。
3. 每個建議請簡短說明，並附上實行建議的理由。

【使用者背景】：
{user_profile_json}

【本題內容】：
{question_text}

【學習目標】：
{learning_goal}

【使用者回覆】：
{user_answer or '（尚未填寫）'}

請用以下格式輸出：
1. 建議 A...
2. 建議 B...
👉 鼓勵語句
"""

    try:
        reply = call_gpt(prompt=prompt)
        return reply.strip()
    except Exception as e:
        return f"⚠️ 無法產生建議：{e}"
