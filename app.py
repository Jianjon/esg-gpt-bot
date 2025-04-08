import streamlit as st
st.set_page_config(page_title="ESG 淨零小幫手", page_icon="🌱", layout="centered")

from src.welcome import show_welcome_page

if "user_name" not in st.session_state or not st.session_state.get("intro_survey_submitted"):
    show_welcome_page()
    st.stop()

if "intro_survey_submitted" not in st.session_state:
    st.warning("⚠️ 請先完成 ESG 前導問卷（已整合於 Welcome 頁面）")
    st.stop()

# _init_app 總體處理環境設定與 sys.path
import _init_app

# 套用自定義 CSS 樣式
with open("assets/custom_style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 顯示 Topbar
st.markdown("""
    <style>
        div[data-testid="stAppViewContainer"] > .main {{
            padding-top: 64px;
        }}
    </style>
    <div class="topbar">
        <div class="logo">🌱 ESG Service Path</div>
        <div class="user-info">{}</div>
    </div>
""".format(st.session_state.get("user_name", "未登入").upper()), unsafe_allow_html=True)

from collections import defaultdict
from pathlib import Path
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import faiss
import fitz
import re
from typing import List, Dict, Tuple
from src.utils.prompt_builder import generate_user_friendly_prompt  # 放在這段最上面（只要匯入一次）
from sessions.answer_session import AnswerSession
from sessions.context_tracker import get_conversation, add_context_entry, add_turn
# from sessions.context_tracker import get_all_summaries
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from session_logger import save_to_json, load_from_json, save_to_sqlite
from vector_builder.pdf_processor import PDFProcessor
from vector_builder.metadata_handler import MetadataHandler
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.components.suggest_box import render_suggested_questions

MODULE_MAP = {
    "C": "ESG 教學導入（教學前導）",
    "B": "邊界設定與組織資訊",
    "S": "排放源辨識與確認",
    "D": "數據收集方式與能力",
    "M": "內部管理與SOP現況",
    "R": "報告需求與後續行動"
}

INDUSTRY_FILE_MAP = {
    "餐飲業": "Restaurant.csv",
    "旅宿業": "Hotel.csv",
    "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv",
    "物流業": "Logistics.csv",
    "辦公室服務業": "Offices.csv"
}

STAGE_MAP = {
    "basic": "beginner",
    "advanced": "intermediate"
}

TOPIC_ORDER = [
    "ESG 教學導入（教學前導）",
    "邊界設定與組織資訊",
    "排放源辨識與確認",
    "數據收集方式與能力",
    "內部管理與SOP現況",
    "報告需求與後續行動"
]

def load_questions(industry: str, stage: str = "basic", skip_common: bool = False) -> list:
    filename = INDUSTRY_FILE_MAP.get(industry)
    if not filename:
        raise ValueError(f"找不到產業對應的題庫：{industry}")
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到題庫檔案：{path}")

    df = pd.read_csv(path)
    required_cols = ["question_id", "question_text", "difficulty_level", "option_type", "answer_tags"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"題庫缺少必要欄位：{col}")

    if stage not in STAGE_MAP:
        raise ValueError(f"輸入值錯誤：stage 應為 basic 或 advanced，但收到：{stage}")
    mapped_stage = STAGE_MAP[stage]
    df = df[df["difficulty_level"].isin([mapped_stage] if stage == "basic" else ["beginner", "intermediate"])]

    questions = []
    for _, row in df.iterrows():
        qid = row["question_id"]
        topic = row.get("topic_category", "").strip() or MODULE_MAP.get(qid[0], "未分類")
        options, option_notes = [], {}
        for opt in ["A", "B", "C", "D", "E"]:
            val = row.get(f"option_{opt}")
            if pd.notna(val):
                options.append(val)
                option_notes[val] = row.get(f"option_{opt}_note", "")

        questions.append({
            "id": qid,
            "industry": row.get("industry_type", industry),
            "text": row.get("question_text", "未填題目內容"),
            "options": options,
            "option_notes": option_notes,
            "type": row.get("option_type", "single"),
            "topic": topic,
            "difficulty": row.get("difficulty_level", mapped_stage),
            "report_section": row.get("report_section", ""),
            "tags": row.get("answer_tags", "").split("|") if isinstance(row.get("answer_tags"), str) else [],
            "allow_custom_answer": row.get("allow_custom_answer", False),
            "allow_skip": row.get("allow_skip", False),
            "note": row.get("free_answer_note", ""),
            "question_note": row.get("question_note", ""),
            "learning_objective": row.get("learning_objective", ""),
            "report_topic": row.get("report_topic", ""),
            "learning_goal": row.get("learning_goal", ""),
            "follow_up": row.get("follow_up", "")
        })

    if skip_common:
        questions = [q for q in questions if not (q["id"].startswith("C0"))]

    def question_sort_key(q):
        topic_index = TOPIC_ORDER.index(q["topic"]) if q["topic"] in TOPIC_ORDER else 999
        qid = q["id"]
        num_part = int(qid[1:]) if qid[1:].isdigit() else 999
        return (topic_index, num_part)

    return sorted(questions, key=question_sort_key)

# ===== 初始化設定 =====
if "stage" not in st.session_state:
    st.session_state.stage = "basic"
if "jump_to" not in st.session_state:
    st.session_state["jump_to"] = None

user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
current_stage = st.session_state.stage

questions = load_questions(
    industry=st.session_state.industry,
    stage=current_stage,
    skip_common=True
)

if "session" not in st.session_state:
    session_file = Path("data/sessions") / f"{st.session_state.company_name}_{st.session_state.user_name}.json"
    if session_file.exists():
        if st.session_state.get("reset_data"):
            session_file.unlink()
            st.toast("✅ 已清除原有紀錄，問卷將從頭開始。")
            st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)
        else:
            session = load_from_json(user_id, questions)
            if session:
                if st.button("🔄 繼續上次答題進度"):
                    st.session_state.session = session
                    st.rerun()
                else:
                    st.warning("偵測到您有未完成的問卷紀錄，您可以選擇繼續或重新開始。")
                    st.stop()
    else:
        st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)

session = st.session_state.session
current_q = session.get_current_question()

# ===== 啟用 jump_to 跳題 =====
if st.session_state.get("jump_to"):
    qid = st.session_state["jump_to"]
    index = next((i for i, item in enumerate(session.question_set) if item["id"] == qid), None)
    if index is not None:
        session.jump_to(index)
        st.session_state["jump_to"] = None
        st.rerun()

# ===== 側邊列重構（使用 question_set） =====
with st.sidebar:
    st.title("📋 ESG Service Path | 淨零小幫手")
    st.markdown("---")
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state.user_name}")
    st.markdown(f"**階段：** {'初階' if st.session_state.stage == 'basic' else '進階'}")
    st.markdown(f"**目前進度：** {session.current_index + 1} / {len(session.question_set)}")
    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    current_topic = current_q.get("topic") if current_q else None
    answered_ids = {r["question_id"] for r in session.responses}

    questions_by_topic = defaultdict(list)
    for q in session.question_set:
        topic = q.get("topic", "未分類")
        questions_by_topic[topic].append(q)

    for topic, q_list in questions_by_topic.items():
        total = len(q_list)
        answered = sum(1 for q in q_list if q["id"] in answered_ids)
        checked = "✅ " if answered == total else ""
        expanded = topic == current_topic

        with st.expander(f"{checked}{topic}", expanded=expanded):
            for idx, q in enumerate(q_list, 1):
                is_done = q["id"] in answered_ids
                label = f"{idx}. {q.get('text', '')[:15]}..."
                if is_done:
                    label += " ✔"

                key = f"jump_to_{q['id']}"
                if st.button(label, key=key):
                    st.session_state["jump_to"] = q["id"]
                    st.rerun()


# 固定主體容器
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)

# 顯示顧問引導
friendly_intro = generate_user_friendly_prompt(current_q, st.session_state.user_intro_survey)

st.markdown("#### 💬 顧問引導")
st.markdown(f"**{friendly_intro}**")  # ✅ 顯示粗體引導語

# 主體內容：問題主體、說明與選項
if current_q:
    # ===== 顯示學習目標 =====
    goal = current_q.get("learning_goal", "")
    st.markdown("#### 🎯 學習目標")
    st.markdown(f"<p style='font-size:18px'><strong><em>{goal}</em></strong></p>", unsafe_allow_html=True)

    #===== 顯示題目主文 =====
    st.markdown("---")
    st.markdown("### 📝 題目")
    st.markdown(f"<p style='font-size:18px'><strong>{current_q.get('text', '')}</strong></p>", unsafe_allow_html=True)

    st.markdown("  \n")
    # ===== 顯示題目說明（若有）=====
    note = current_q.get("question_note", "")
    if note:
        st.markdown("#### 🗒️ 題目說明")
        st.markdown(f"<div style='font-size:16px'>{note}</div>", unsafe_allow_html=True)

    st.markdown("  \n")

    # 顯示選項們
    options = current_q["options"]
    option_notes = current_q.get("option_notes", {})

    formatted_options = []
    for opt in options:
        note = option_notes.get(opt, "")
        html = f"<strong>{opt}</strong>：<span style='font-size:15px'>{note}</span>"
        formatted_options.append(html)

    selected = []

    if current_q["type"] == "single":
        selected_html = st.radio("可選擇：", formatted_options, format_func=lambda x: x, index=0, key="radio_options", label_visibility="visible")
        if selected_html:
            selected = [options[formatted_options.index(selected_html)]]
    else:
        st.markdown("可複選：")
        for i, html in enumerate(formatted_options):
            opt_key = options[i]
            if st.checkbox(html, key=opt_key):
                selected.append(opt_key)
    # ✅ 若允許使用者自訂答案
    custom_input = ""
    if current_q.get("allow_custom_answer", False):
        st.markdown("#### ✍️ <strong>若以上選項都不合適，請填寫您的自訂答案：</strong>", unsafe_allow_html=True)
        custom_input = st.text_input("請輸入您的想法或做法...", key="custom_input")

import streamlit as st
from src.utils.prompt_builder import build_learning_prompt, generate_user_friendly_prompt
from src.utils.gpt_tools import call_gpt

# 假設的問題資料和用戶輸入
current_q = {"id": "q1", "type": "single", "question": "你的公司是否關注 ESG 議題？"}
selected = st.selectbox("選擇答案：", ["是", "否"])
selected = [selected]
custom_input = st.text_input("如果有其他想法，請輸入：", value="")

# 確保必要的變數已定義
if "user_intro_survey" not in st.session_state:
    st.session_state.user_intro_survey = {"background": "未知"}

# 生成介紹性回應
friendly_intro = generate_user_friendly_prompt(current_q, st.session_state.user_intro_survey)
st.write("介紹：", friendly_intro)

# 後續的 GPT 教學邏輯
if custom_input:
    selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]

user_profile = {
    "user_name": st.session_state.get("user_name", ""),
    "company_name": st.session_state.get("company_name", ""),
    "industry": st.session_state.get("industry", ""),
    **st.session_state.get("user_intro_survey", {})
}

# 構建 prompt
prompt_text = build_learning_prompt(user_profile, current_q, user_answer)

# 按鈕觸發 GPT 回應（補充第一段的按鈕）
if st.button("🤖 由 ESG 小幫手產生教學引導", key="btn_gpt_teaching"):
    with st.chat_message("assistant"):
        with st.spinner("AI 教學中，請稍候..."):  # 使用第二段的提示訊息
            try:
                gpt_reply = call_gpt(prompt_text, temperature=0.7)
                st.markdown(gpt_reply)
                add_turn(current_q["id"], prompt_text, gpt_reply)
            except Exception as e:
                st.error(f"⚠️ GPT 回覆失敗：{str(e)}")

    # 導航按鈕區塊
    st.markdown("---")
    st.markdown("#### 🧭 請確認您的作答，然後點擊「下一題」或返回修改：")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ 上一題", key="btn_prev", use_container_width=True):
            session.go_back()
            st.rerun()

    with col2:
        if st.button("➡️ 下一題（提交答案）", key="btn_next", use_container_width=True):
            if current_q["type"] == "single":
                answer_payload = selected[0] if selected else ""
            else:
                answer_payload = selected

            if custom_input:
                answer_payload = [custom_input] if current_q["type"] == "single" else selected + [custom_input]

            if not answer_payload:
                st.warning("⚠️ 請先選擇或填寫一個答案後再繼續")
                st.stop()

            result = session.submit_response(answer_payload)
            add_context_entry(current_q["id"], answer_payload, current_q["text"])
            save_to_json(session)

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ 已提交，即將跳轉至下一題")
                st.rerun()

    st.markdown("  \n")
    # === GPT 對話式問答區塊 ===
    st.divider()
    st.markdown("#### 🤖 淨零小幫手（測試階段以五題為限）")

    # 初始化對話記憶
    if "qa_threads" not in st.session_state:
        st.session_state.qa_threads = {}

    chat_id = current_q["id"]
    from sessions.context_tracker import get_conversation, add_turn
    from src.utils.gpt_tools import call_gpt

    # 顯示歷史對話
    for msg in get_conversation(chat_id):
        if "user" in msg:
            with st.chat_message("user"):
                st.markdown(msg["user"])
        if "gpt" in msg:
            with st.chat_message("assistant"):
                st.markdown(msg["gpt"])



    # 定義點按按鈕後自動送出的處理流程
    def auto_submit_prompt(selected_prompt):
        from src.utils.gpt_tools import call_gpt
        from sessions.context_tracker import add_turn, get_conversation

        with st.chat_message("user"):
            st.markdown(selected_prompt)
        with st.chat_message("assistant"):
            with st.spinner("AI 回覆中..."):
                context_text = f"{current_q['text']}\n{current_q.get('learning_goal', '')}"
                reply = call_gpt(
                prompt=selected_prompt,
                question_text=current_q["text"],
                learning_goal=current_q.get("learning_goal", ""),
                chat_history=get_conversation(current_q["id"]),
                industry=st.session_state.get("industry", "")
            )

                st.markdown(reply)
                add_turn(current_q["id"], selected_prompt, reply)

    # 💡 自動從題目帶入建議提問（支援自然語句格式）
    suggested_prompts_raw = current_q.get("follow_up", "")
    suggested_prompts = [
        s.strip() + "？"
        for s in suggested_prompts_raw.split("？")
        if s.strip()
]

    # 建議提問按鈕區
    st.markdown("#### 💬 想深入了解？可點選以下問題繼續提問：")
    render_suggested_questions(suggested_prompts, auto_submit_prompt)




    # 下方輸入框
    if prompt := st.chat_input("針對本題還有什麼問題？可詢問 ESG 顧問 AI"):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI 回覆中..."):
                try:
                    reply = call_gpt(prompt)  
                    st.markdown(reply)
                    add_turn(chat_id, prompt, reply)
                except Exception as e:
                    st.error(f"⚠️ AI 回覆失敗：{str(e)}")

 
else:  # 確保這裡的 else 與上方 if 對齊
    st.success("🎉 您已完成本階段問卷！")
    baseline = BaselineManager("data/baselines/company_abc.json").get_baseline()
    summary = session.get_summary(company_baseline=baseline)
    summary["user_name"] = st.session_state.get("user_name")
    summary["company_name"] = st.session_state.get("company_name")
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []))

    st.markdown("## 📄 診斷摘要報告")
    st.markdown(f"""
```
{report.generate_text_report()}
```
""")

    st.markdown("## 💡 題目建議與改善方向")
    for fb in feedback_mgr.generate_feedback():
        st.markdown(f"- **{fb['question_id']} 建議：** {fb['feedback']}")

    st.markdown("## 📌 總體建議")
    st.markdown(feedback_mgr.generate_overall_feedback())

    save_to_json(session)
    save_to_sqlite(session)

    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 您已完成初階診斷，是否進入進階問卷？")
        if st.button("👉 進入進階問卷"):
            st.session_state.stage = "advanced"
            new_qset = load_questions(st.session_state.industry, "advanced", skip_common=True)
            st.session_state.session = AnswerSession(user_id=user_id, question_set=new_qset)
            st.rerun()

# 向量處理（暫保留）
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "!", "?", "！", "？"],
    keep_separator=True
)

base_dir = Path("data/db_pdf_data")

class ChunkMetadata:
    def __init__(self, pdf_path: Path, page: int, section: int, base_dir: Path):
        self.chunk_id = f"{pdf_path.stem}-p{page}-s{section}"
        self.source = pdf_path.name
        self.path = str(pdf_path.parent.relative_to(base_dir))
        self.main_topic = ""
        self.industry = ""
        self.region = ""
        self.page = page
        self.title = ""
        self.language = ""

class VectorStore:
    def __init__(self):
        self.dimension = 1536
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    def add_vectors(self, vectors, metadata_list):
        self.index.add(vectors)
        self.metadata.extend(metadata_list)

    def save(self, output_dir: Path):
        faiss.write_index(self.index, str(output_dir / 'faiss_index.index'))
        with open(output_dir / 'chunk_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)

# 📄 app.py

import streamlit as st
from src.loaders.question_loader import load_questions  # 正確引用此函式

def show_learning_page():
    # 讀取 session_state 中的階段與產業資料
    stage = st.session_state.get("stage", "basic")  # 默認為初階
    industry = st.session_state.get("industry", "餐飲業")  # 默認為餐飲業

    # 根據階段載入題目
    questions = load_questions(industry=industry, stage=stage)

    st.markdown("## 🎯 開始您的 ESG 學習之旅")
    st.markdown("""
    歡迎來到學習頁面！這裡是為您量身設計的學習路徑，讓我們開始探索如何進行碳盤查、了解 ESG 的核心概念，並幫助您與企業合作減碳。
    """)

    # 顯示學習內容
    st.markdown("### 學習模組 1: 碳盤查概述")
    st.markdown("在這個模組中，您將學到如何進行碳盤查、什麼是碳足跡...")

    # 顯示題目，依照 `stage` 顯示對應題目
    st.markdown("### 這是您的問卷題目：")
    for question in questions:
        st.markdown(f"**{question['text']}**")  # 顯示問題
        for option in question["options"]:  # 顯示選項
            st.markdown(f"- {option}")

import streamlit as st

