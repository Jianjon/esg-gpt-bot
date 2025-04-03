import streamlit as st
from sessions.answer_session import AnswerSession
from sessions.context_tracker import add_context_entry, get_all_summaries
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from loaders.question_loader import load_questions
from session_logger import save_to_json, load_from_json, save_to_sqlite
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path
import logging
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
import re
from vector_builder import PDFProcessor, MetadataHandler

load_dotenv()

st.set_page_config(page_title="ESG 問卷診斷", layout="wide")
st.title("📋 ESG 智能問卷診斷 | 淨零小幫手")

# --- 基本驗證 ---
if "user_name" not in st.session_state or "industry" not in st.session_state:
    st.warning("請先從 welcome.py 進入並填寫基本資訊。")
    st.stop()

if "stage" not in st.session_state:
    st.session_state.stage = "basic"

# --- 問題與使用者 ID 初始化 ---
user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
question_set = load_questions(st.session_state.industry, st.session_state.stage)

# --- Session 初始化或載入 ---
if "session" not in st.session_state:
    session = load_from_json(user_id, question_set)
    if session:
        if st.button("🔄 繼續上次答題進度"):
            st.session_state.session = session
            st.rerun()
        else:
            st.warning("偵測到您有未完成的問卷記錄，您可以選擇繼續或重新開始。")
            st.stop()
    else:
        st.session_state.session = AnswerSession(user_id=user_id, question_set=question_set)

session = st.session_state.session
current_q = session.get_current_question()

# --- 側邊欄 ---
with st.sidebar:
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state.user_name}")
    st.markdown(f"**Email：** {st.session_state.get('user_email', '-')}")
    st.markdown(f"**公司：** {st.session_state.company_name}")
    st.markdown(f"**產業類別：** {st.session_state.industry}")
    st.markdown(f"**階段：** {'初階' if st.session_state.stage == 'basic' else '進階'}")
    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")
    topic_progress = session.get_topic_progress()
    topics = list(topic_progress.keys())
    answered = [v["answered"] for v in topic_progress.values()]
    totals = [v["total"] for v in topic_progress.values()]
    fig, ax = plt.subplots()
    ax.barh(topics, totals, color="#eee", label="總題數")
    ax.barh(topics, answered, color="#4CAF50", label="已完成")
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)

# --- 問卷流程 ---
progress = session.get_progress()
st.progress(progress["percent"] / 100, text=f"目前進度：{progress['answered']} / {progress['total']} 題")

if current_q:
    st.markdown(f"### ❓ 問題 {session.current_index + 1}")
    st.markdown(current_q["text"])

    if current_q["type"] == "single":
        response = st.radio("請選擇一個選項：", current_q["options"])
    else:
        response = st.multiselect("可複選：", current_q["options"])

    if st.button("✅ 提交回答"):
        result = session.submit_response(response)
        add_context_entry(current_q["id"], response, current_q["text"])
        save_to_json(session)
        if "error" in result:
            st.error(result["error"])
        else:
            st.rerun()
else:
    st.success("🎉 您已完成本階段問卷！")
    baseline = BaselineManager("data/baselines/company_abc.json").get_baseline()
    summary = session.get_summary(company_baseline=baseline)
    summary["user_name"] = st.session_state.get("user_name")
    summary["company_name"] = st.session_state.get("company_name")
    report = ReportManager(summary)
    feedback_mgr = FeedbackManager(summary.get("comparison", []))

    st.markdown("## 📄 診斷摘要報告")
    st.markdown(f"```\n{report.generate_text_report()}\n```")

    st.markdown("## 💡 題目建議與改善方向")
    for fb in feedback_mgr.generate_feedback():
        st.markdown(f"- **{fb['question_id']} 建議：** {fb['feedback']}")

    st.markdown("## 📌 總體建議")
    st.markdown(feedback_mgr.generate_overall_feedback())

    save_to_json(session)
    save_to_sqlite(session)

    # 進入進階診斷
    if st.session_state.stage == "basic":
        st.divider()
        st.subheader("🚀 您已完成初階診斷，是否進入進階階段？")
        if st.button("👉 進入進階問卷"):
            st.session_state.stage = "advanced"
            new_qset = load_questions(st.session_state.industry, "advanced")
            st.session_state.session = AnswerSession(user_id=user_id, question_set=new_qset)
            st.rerun()

# 設置 OpenAI API
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1536
)

# 設置文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "!", "?", "！", "？"],
    keep_separator=True
)

# 主要處理流程
def process_pdf(pdf_path: Path):
    # 1. 讀取 PDF
    # 2. 分段
    # 3. 生成 metadata
    # 4. 建立向量
    # 5. 儲存到 FAISS
    pass

class ChunkMetadata:
    def __init__(self, pdf_path: Path, page: int, section: int):
        self.chunk_id = f"{pdf_path.stem}-p{page}-s{section}"
        self.source = pdf_path.name
        self.path = str(pdf_path.parent.relative_to(base_dir))
        self.main_topic = self._extract_topic(pdf_path)
        self.industry = self._extract_industry(pdf_path)
        self.region = self._extract_region(pdf_path)
        self.page = page
        self.title = ""  # 從 PDF 提取
        self.language = self._detect_language()

class VectorStore:
    def __init__(self):
        self.dimension = 1536
        self.index = faiss.IndexFlatIP(self.dimension)  # cosine similarity
        self.metadata = []
    
    def add_vectors(self, vectors, metadata_list):
        self.index.add(vectors)
        self.metadata.extend(metadata_list)
    
    def save(self, output_dir: Path):
        faiss.write_index(self.index, str(output_dir / 'faiss_index.index'))
        with open(output_dir / 'chunk_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)

def main():
    # 設置日誌
    logging.basicConfig(
        filename='data/vector_output/build_log.txt',
        level=logging.INFO
    )
    
    # 建立輸出目錄
    output_dir = Path('data/vector_output')
    output_dir.mkdir(exist_ok=True)
    
    # 處理每個資料夾
    base_dir = Path('data/db_pdf_data')
    for folder in ['cases', 'international', 'taiwan']:
        process_folder(base_dir / folder)

    # 在main.py中使用
    pdf_processor = PDFProcessor()
    metadata_handler = MetadataHandler()

    def process_single_pdf(pdf_path: Path):
        # 處理PDF並獲取chunks
        chunks_with_metadata = pdf_processor.process_pdf(pdf_path)
        
        # 擴充metadata
        enriched_chunks = []
        for chunk, metadata in chunks_with_metadata:
            enriched_metadata = metadata_handler.enrich_metadata(metadata, chunk)
            enriched_chunks.append((chunk, enriched_metadata))
        
        return enriched_chunks
