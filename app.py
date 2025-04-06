import streamlit as st

# 🧱 Step 1：設定頁面（一定要是第一個 Streamlit 指令）
st.set_page_config(page_title="ESG 問卷評斷", layout="centered")

# 🧠 Step 2：初始化所有 session_state 欄位（✅ 這段你寫得很好）
if "qa_threads" not in st.session_state:
    st.session_state.qa_threads = {}

if "context_history" not in st.session_state:
    st.session_state.context_history = []

if "guided_chat" not in st.session_state:
    st.session_state.guided_chat = []

if "guided_turns" not in st.session_state:
    st.session_state.guided_turns = 0

# 🧩 Step 3：先定義會用到的小工具函數（你寫的 get_conversation 與 add_turn 就放這邊）
from typing import List, Dict

def get_conversation(question_id: str) -> List[Dict[str, str]]:
    return st.session_state.qa_threads.get(question_id, [])

def add_turn(question_id: str, user_input: str, assistant_reply: str):
    if question_id not in st.session_state.qa_threads:
        st.session_state.qa_threads[question_id] = []
    st.session_state.qa_threads[question_id].append({
        "user": user_input,
        "assistant": assistant_reply
    })

# 🏗️ Step 4：其他系統初始化，例如 _init_app、CSS 載入
import _init_app
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

# 檢查是否須先顯示 welcome 页面
if "user_name" not in st.session_state or "industry" not in st.session_state:
    from welcome import show_welcome
    show_welcome()
    st.stop()

# 檢查是否已完成基本資訊填寫
if "welcome_submitted" not in st.session_state or not st.session_state["welcome_submitted"]:
    st.warning("請先完成產業選擇與公司基本資料填寫。")
    st.stop()

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

# --- Session 管理 ---
from src.sessions.answer_session import AnswerSession
from src.sessions.context_tracker import add_context_entry
from src.session_logger import save_to_json, load_from_json, save_to_sqlite

# --- GPT 與提示模組 ---
from src.managers.gpt_rewrite import rewrite_question_to_conversational
from src.utils.gpt_tools import call_gpt
from src.question_router import recommend_next_question

# --- 分析報告與建議 ---
from src.managers.baseline_manager import BaselineManager
from src.managers.report_manager import ReportManager
from src.managers.feedback_manager import FeedbackManager

# --- 向量處理（PDF 建檔用） ---
# from src.vector_builder.pdf_processor import PDFProcessor
# from src.vector_builder.metadata_handler import MetadataHandler


# --- 向量嵌入與分段工具 ---
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils.gpt_tools import call_gpt

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
    st.title("📋 ESG 智能問卷診斶 | 淨零小幫手")
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

# 匯入進度圖相關模組
from src.utils.topic_progress import get_topic_progress

# 計算已回答的題目 ID
answered_ids = {r["question_id"] for r in session.responses}

# 生成進度圖
fig = get_topic_progress(session.question_set, answered_ids)

# 在側邊欄顯示進度圖
st.sidebar.pyplot(fig)

# 固定主體容器
st.markdown('<div class="main-content-container">', unsafe_allow_html=True)

# 匯入 context_tracker
from src.sessions import context_tracker

# 主體內容：問題主體、說明與選項
if current_q:
    st.markdown(f"#### 🎯 學習主題：<br>{current_q.get('learning_goal', '')}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<h3>{current_q.get('text', '')}</h3>", unsafe_allow_html=True)
    st.markdown(f"**題目說明：** {current_q.get('question_note', '')}")

    # ===== 顯示選項 =====
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
    st.markdown("---")

    # --- AI 對話提示語區塊（顯示 follow_up，引導使用者提問） ---
    if current_q.get("follow_up"):
        ai_hint = f"💡 顧問提醒：{current_q['follow_up']} 若您對此有疑問，可在下方輸入。"
    else:
        ai_hint = "💡 您可以在下方輸入任何想法或問題，AI 將提供協助。"

    st.markdown(f"<div class='ai-message'>{ai_hint}</div>", unsafe_allow_html=True)

    # ===== 顯示過去對話紀錄 =====
    history = context_tracker.get_conversation(current_q["id"])
    for turn in history:
        st.markdown(f"<div class='user-message'>🧑 {turn['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-message'>🤖 {turn['assistant']}</div>", unsafe_allow_html=True)

    # ===== 使用者輸入框與提交按鈕 =====
    user_input = st.text_area("💬 若有想法或問題，請輸入並提交：", placeholder="輸入您的問題或想法...", height=80)
    submit_button = st.button("提交問題")

    if submit_button and user_input.strip():
        # ⛳ 根據題目內容與 follow_up 自動組 prompt
        follow_up = current_q.get("follow_up", "")
        full_prompt = f"{follow_up}\n\n使用者提問：{user_input}" if follow_up else user_input

        # 呼叫 GPT 模型（使用 consult_chat_app 中的邏輯）
        from src.consult_chat_app import call_gpt
        gpt_reply = call_gpt(full_prompt)

        # 儲存到對話紀錄
        context_tracker.add_turn(current_q["id"], user_input, gpt_reply)

        # 立即顯示新的回答
        st.markdown(f"<div class='user-message'>🧑 {user_input}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-message'>🤖 {gpt_reply}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



    # ===== 導航按鈕區塊 =====
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
                # 🧠 加入 GPT 的行動建議摘要
                from src.sessions import context_tracker  # 若上面已有就不需重複 import
                action = context_tracker.generate_following_action(current_q["id"])
                if action:
                    st.session_state.context_history.append({
                        "id": current_q["id"],
                        "summary": action
                    })

                # 換下一題
                st.rerun()


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
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1536
)

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