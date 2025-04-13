# src/utils/report_utils.py

import json
from typing import List, Dict
from src.utils.gpt_tools import call_gpt
import streamlit as st


def generate_user_background_section(user_intro_data: dict) -> str:
    """
    根據使用者前導問卷資料，產出報告中「使用者背景說明」段落。
    """
    lines = []
    for key, value in user_intro_data.items():
        lines.append(f"- **{key}**：{value}")
    return "### 👤 使用者背景摘要\n" + "\n".join(lines)


def get_sorted_context_history() -> List[Dict[str, str]]:
    """
    依照問卷順序回傳使用者的作答摘要（避免因跳題導致報告順序錯亂）
    """
    if "session" not in st.session_state:
        return st.session_state.get("context_history", [])

    order_map = {q["id"]: i for i, q in enumerate(st.session_state.session.question_set)}
    return sorted(
        st.session_state.get("context_history", []),
        key=lambda x: order_map.get(x["id"], 999)
    )


def generate_full_gpt_report(
    user_profile: dict,
    context_history: List[dict],
    tone: str = "professional"
) -> str:
    """
    使用 GPT-4 產出完整的診斷報告，包括企業現況總結與具體建議行動方案。
    """
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    context_summary = "\n".join([f"Q: {c['id']} | {c['summary']}" for c in context_history])

    style_instruction = {
        "gentle": "語氣請溫和鼓勵，像是在陪伴企業主一起成長。",
        "professional": "語氣請專業簡潔，像在為主管做簡報。",
        "creative": "語氣請跳脫傳統，用啟發式語言引導企業思考未來。"
    }.get(tone, "語氣請專業簡潔，像在為主管做簡報。")

    prompt = f"""
你是一位專業 ESG 顧問，擅長針對中小企業碳盤查狀況進行診斷與建議。
請根據以下資料，撰寫一份 **完整的 ESG 診斷報告**，字數約 600～800 字。

🌟【目標主題】：碳盤查初步診斷與碳管理建議  
👨‍💼【使用者背景】：{user_profile_json}  
📜【問卷摘要紀錄】：\n{context_summary}

🖍️【撰寫規則】
1. 開頭請簡短說明報告目的與適用場景。
2. 第一段至第二段請整理企業的 ESG 現況與潛在風險（根據作答摘要歸納）。
3. 接著提出 3～5 點「具體的碳管理行動建議」，可條列、分點敘述。
4. 最後以鼓勵語氣結尾，並可提出未來進階指引（例如：進一步的碳足跡計算、SOP 建立等）。
5. 報告應具備正式專業語氣，但用詞易懂，便於企業主理解。

{style_instruction}

⚠️ 請直接產出報告內容，不要補充說明，不需要說你是 AI。
    """

    return call_gpt(prompt, model="gpt-4").strip()
