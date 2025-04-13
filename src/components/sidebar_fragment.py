# src/components/sidebar_fragment.py

import streamlit as st
from collections import defaultdict
from typing import List, Dict
from src.utils.report_utils import generate_full_gpt_report
from src.managers.profile_manager import get_user_profile

user_profile = get_user_profile()

@st.fragment
def render_sidebar_fragment(session, current_q):
    st.title("📋 ESG Service Path")
    st.markdown("---")
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state.get('user_name', '未登入')}")
    st.markdown(f"**階段：** {'初階' if st.session_state.get('stage') == 'basic' else '進階'}")

    # ✅ 進度顯示改為「已作答題數」
    answered_ids = {r["question_id"] for r in session.responses}
    total_questions = len(session.question_set)
    answered = len(answered_ids)
    st.markdown(f"**目前進度：** {answered} / {total_questions} 題")

    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    current_topic = current_q.get("topic", "")
    topic_groups = defaultdict(list)
    for q in session.question_set:
        topic_groups[q["topic"]].append(q)

    for topic, q_list in topic_groups.items():
        total = len(q_list)
        topic_answered = sum(1 for q in q_list if q["id"] in answered_ids)
        checked = "✅ " if topic_answered == total else ""
        expanded = topic == current_topic

        with st.expander(f"{checked}{topic}", expanded=expanded):
            for i, q in enumerate(q_list):
                qid = q["id"]
                is_answered = qid in answered_ids
                label_key = f"label_{qid}"
                label = st.session_state.get(label_key, q["text"][:12].strip())
                display_label = f"{'✔️ ' if is_answered else ''}{i+1}. {label}"

                if st.button(display_label, key=f"jump_to_{qid}"):
                    st.session_state["jump_to"] = qid
                    st.session_state["_trigger_all_sections"] = st.session_state.get("_trigger_all_sections", 0) + 1

    # === 報告區塊 ===
    st.markdown("---")
    st.subheader("🧾 測驗診斷報告")
    st.caption(f"Debug：已回答 {answered} 題 / 共 {total_questions} 題")

    REQUIRED_QUESTIONS = 10
    if answered < REQUIRED_QUESTIONS:
        st.info(f"⚠️ 請先完成至少 {REQUIRED_QUESTIONS} 題，才能查看診斷報告。\n\n💡 建議完整參與 AI 顧問教學互動，讓報告更貼近您的情境與需求。")
    else:
        if st.button("📄 產出目前報告（GPT-4）"):
            with st.spinner("AI 顧問分析中..."):
                try:
                    context_history = st.session_state.get("context_history", [])
                    tone = st.session_state.get("preferred_tone", "professional")
                    report = generate_full_gpt_report(user_profile, context_history, tone=tone)
                    st.success("✅ 報告產出完成！")
                    st.markdown(report)
                except Exception as e:
                    st.error(f"❌ 報告產出失敗：{e}")
