# src/components/sidebar_fragment.py

import streamlit as st
from collections import defaultdict
from typing import List, Dict
from src.utils.report_utils import generate_full_gpt_report
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

@st.fragment
def render_sidebar_fragment(session, current_q, key=None):  # ← 多這個 key=None
    st.title("📋 ESG Service Path：淨零GPT")
    st.markdown("---")

    # === 使用者資訊 ===
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state.get('user_name', '未登入')}")
    st.markdown(f"**階段：** {'初階' if st.session_state.get('stage') == 'basic' else '進階'}")

    # === 問卷進度統計（抽成函式） ===
    answered = render_question_progress(session)

    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    # === 主題分類與勾選進度 ===
    current_topic = current_q.get("topic", "")
    topic_groups = defaultdict(list)
    for q in session.question_set:
        topic_groups[q["topic"]].append(q)

    if "jump_to" not in st.session_state:
        st.session_state["jump_to"] = None

    for topic, q_list in topic_groups.items():
        total = len(q_list)
        answered_ids = {r["question_id"] for r in session.responses}
        topic_answered = sum(1 for q in q_list if q["id"] in answered_ids)
        checked = "✅ " if topic_answered == total else ""
        expanded = topic == current_topic

        with st.expander(f"{checked}{topic}", expanded=expanded):
            for i, q in enumerate(q_list):
                qid = q["id"]
                is_answered = qid in answered_ids
                display_text = q.get("text", "").strip().replace("\n", " ")
                short_label = display_text[:16] + "..." if len(display_text) > 16 else display_text
                prefix = "✔️" if is_answered else "▫️"
                label = f"{prefix} {i + 1}. {short_label}"

                if st.button(label, key=f"jump_to_{qid}", use_container_width=True):
                    st.session_state["jump_to"] = qid
                    st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1
                    st.rerun()

    # === 報告產出區塊 ===
    st.markdown("---")
    st.subheader("🧾 測驗診斷報告")

    REQUIRED_QUESTIONS = 10
    if answered < REQUIRED_QUESTIONS:
        st.info(
            f"⚠️ 請先完成至少 {REQUIRED_QUESTIONS} 題，才能查看診斷報告。\n\n"
            "💡 建議完整參與 AI 顧問教學互動，讓報告更貼近您的情境與需求。"
        )
    else:
        if st.button("📄 產出目前報告（GPT-4）", use_container_width=True):
            context_history = st.session_state.get("context_history", [])
            if not context_history:
                st.warning("⚠️ 尚未有任何 AI 回饋紀錄，請先完成至少一題互動後再產出報告。")
            else:
                with st.spinner("AI 顧問分析中..."):
                    try:
                        tone = st.session_state.get("preferred_tone", "professional")
                        report = generate_full_gpt_report(user_profile, context_history, tone=tone)
                        st.success("✅ 報告產出完成！")
                        st.markdown(report)
                    except Exception as e:
                        st.error(f"❌ 報告產出失敗：{e}")

# === 抽出的進度函式 ===
def render_question_progress(session) -> int:
    answered_ids = {r["question_id"] for r in session.responses}
    total_questions = len(session.question_set)
    answered = len(answered_ids)

    st.markdown(f"**目前進度：** {answered} / {total_questions} 題")
    st.progress(answered / total_questions if total_questions else 0)

    # Debug 可選：顯示已答題 ID
    st.caption(f"🧪 已作答題目 ID：{list(answered_ids)}")
    return answered
