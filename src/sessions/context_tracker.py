import openai
from typing import List, Dict
import streamlit as st
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化記憶結構
if "context_history" not in st.session_state:
    st.session_state["context_history"] = []
if "qa_threads" not in st.session_state:
    st.session_state["qa_threads"] = {}
if "guided_chat" not in st.session_state:
    st.session_state["guided_chat"] = []
if "guided_turns" not in st.session_state:
    st.session_state["guided_turns"] = 0

# --- Context 紀錄 ---
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

        st.session_state["context_history.append"]({
            "id": question_id,
            "answer": answer_text,
            "summary": summary
        })
        return summary

    except Exception as e:
        print(f"⚠️ GPT 摘要失敗：{e}")
        return "（摘要失敗）"

def get_all_summaries() -> List[str]:
    """
    從 `qa_threads` 中獲取所有問題的摘要（最後一輪回答）。
    """
    return [
        f"Q{q_id}：{st.session_state.qa_threads[q_id][-1]['assistant']}"
        for q_id in st.session_state.qa_threads
    ]

# sessions/context_tracker.py

def get_previous_summary(question_id: str) -> str:
    context = st.session_state.get("context_history", [])
    for entry in reversed(context):
        if entry["question_id"] != question_id:
            return entry.get("summary", "")
    return ""



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

# --- 自動產生後續建議 ---
def generate_following_action(question_id: str) -> str:
    """
    根據該題的使用者背景、作答摘要與對話歷程，自動產出下一步可行建議
    """
    history = st.session_state.qa_threads.get(question_id, [])
    chat_log = "\n".join([
        f"使用者：{turn['user']}\nAI：{turn['assistant']}"
        for turn in history
    ]) if history else "（無對話紀錄）"

    # 使用者背景資訊
    user_profile = st.session_state.get("user_intro_survey", {})
    role = user_profile.get("q4", "使用者")
    motivation = user_profile.get("q2", "")
    experience = user_profile.get("q5", "")
    industry = st.session_state.get("industry", "某產業")

    # 擷取該題摘要
    summary = next(
        (s["summary"] for s in st.session_state.get("context_history", []) if s["id"] == question_id),
        "使用者已完成本題作答，正在尋找後續方向。"
    )

    prompt = f"""
你是一位 ESG 顧問助理，請根據下列資訊，幫助企業提出一段具體可行的後續建議（最多 100 字）：

【使用者背景】
- 產業：{industry}
- 角色：{role}
- 動機：{motivation}
- 經驗：{experience}

【本題摘要】
{summary}

【對話紀錄】
{chat_log}

請以「建議：」開頭，用口語化且實務導向的語氣，輸出一句話作為行動建議。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位 ESG 顧問助理，協助企業從碳盤查學習中得出後續行動建議。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("⚠️ following action 產生失敗：", e)
        return "（GPT 產生建議失敗）"

def get_previous_summary(current_qid: str) -> str:
    """
    根據目前題目的 ID，從 session_state["context_history"] 找出上一題的摘要。
    若找不到上一題，回傳空字串。
    """
    history = st.session_state.get("context_history", [])
    if not history:
        return ""

    # 找出目前題目的 index
    for idx, entry in enumerate(history):
        if entry.get("question_id") == current_qid:
            if idx > 0:
                return history[idx - 1].get("summary", "")
            else:
                return ""  # 第一題就沒有上一題
    return ""  # 沒找到目前題目
