import streamlit as st

if "user_name" not in st.session_state:
    st.switch_page("1_welcome")
    st.stop()

if "intro_survey_submitted" not in st.session_state:
    st.switch_page("2_intro_survey")
    st.stop()

st.set_page_config(page_title="ESG 問卷評斷", layout="centered")

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

# 固定主體容器
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)

# 主體內容：問題主體、說明與選項
if current_q:
    st.markdown(f"### 👣 目前進度：第 {session.current_index + 1} 題 / 共 {len(session.question_set)} 題")
    st.markdown(f"#### 🎯 學習主題：<br>{current_q.get('learning_goal', '')}", unsafe_allow_html=True)
    st.markdown(f"**題目說明：** {current_q.get('question_note', '')}")
    st.markdown("---")

    # 顯示選項們
    options = current_q["options"]
    option_notes = current_q.get("option_notes", {})
    labeled_options = [f"{opt}：{option_notes.get(opt, '')}" for opt in options]

    selected = []

    if current_q["type"] == "single":
        selected_option = st.radio("可選擇：", labeled_options)
        if selected_option:
            selected = [selected_option.split("：")[0]]
    else:
        st.markdown("可複選：")
        for opt in labeled_options:
            opt_key = opt.split("：")[0]
            if st.checkbox(opt, key=opt_key):
                selected.append(opt_key)
    # ✅ 若允許使用者自訂答案
    custom_input = ""
    if current_q.get("allow_custom_answer", False):
        custom_input = st.text_input("✍️ 或填寫自訂答案：", key="custom_input")

    # 🧠 決定最後送出的答案
    if custom_input:
        selected = [custom_input] if current_q["type"] == "single" else selected + [custom_input]
      

    st.markdown("---")
    # 導航按鈕區塊
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👈 上一題", key="btn_prev", use_container_width=True):
            session.go_back()
            st.rerun()
    with col2:
        if st.button("👉 下一題", key="btn_next", use_container_width=True):
            # 根據題型處理答案格式
            if current_q["type"] == "single":
                answer_payload = selected[0] if selected else ""
            else:
                answer_payload = selected

            # 提交答案
            result = session.submit_response(answer_payload)
            add_context_entry(current_q["id"], selected, current_q["text"])
            save_to_json(session)
            if "error" in result:
                st.error(result["error"])
            else:
                st.rerun()

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

    # 🔵 在 chat_input 上方插入建議問題按鈕區
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

st.set_page_config(page_title="ESG 問卷主流程", layout="centered")

# 進入問卷主畫面（此處開始才進行學習與問答）
st.markdown(f"### 🎯 歡迎 {st.session_state.user_name}，開始 ESG 問答診斷")
# ...載入題庫與主流程邏輯
