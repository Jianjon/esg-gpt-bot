import streamlit as st
st.set_page_config(page_title="ESG 問卷診斷", layout="wide")

# _init_app 將會統一處理環境設定與 sys.path
import _init_app

# 套用自定義樣式（統一在 CSS 控管，確保 block-container 與 chat-input-area 正確）
with open("assets/custom_style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 如果尚未填 welcome 表單，先顯示 welcome 畫面
if "user_name" not in st.session_state or "industry" not in st.session_state:
    from welcome import show_welcome
    show_welcome()
    st.stop()

from sessions.answer_session import AnswerSession
from sessions.context_tracker import add_context_entry, get_all_summaries
from managers.baseline_manager import BaselineManager
from managers.report_manager import ReportManager
from managers.feedback_manager import FeedbackManager
from loaders.question_loader import load_questions, STAGE_MAP
from session_logger import save_to_json, load_from_json, save_to_sqlite
from constants.section_map import MANUAL_SECTION_QUESTIONS
import matplotlib.pyplot as plt
import json
from pathlib import Path
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import fitz  # PyMuPDF

if "stage" not in st.session_state:
    st.session_state.stage = "basic"
if "jump_to" not in st.session_state:
    st.session_state["jump_to"] = None

user_id = f"{st.session_state.get('company_name', 'unknown')}_{st.session_state.get('user_name', 'user')}"
current_stage = st.session_state.stage

questions = load_questions(
    industry=st.session_state.industry,
    stage=current_stage,
    skip_common=True  # ✅ 不載入常識題（C 題）
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
                    st.warning("偵測到您有未完成的問卷記錄，您可以選擇繼續或重新開始。")
                    st.stop()
    else:
        st.session_state.session = AnswerSession(user_id=user_id, question_set=questions)

session = st.session_state.session
current_q = session.get_current_question()

with st.sidebar:
    st.title("📋 ESG 智能問卷診斷 | 淨零小幫手")
    st.markdown("---")
    st.header("👤 使用者資訊")
    st.markdown(f"**姓名：** {st.session_state.user_name}")
    st.markdown(f"**階段：** {'初階' if st.session_state.stage == 'basic' else '進階'}")
    st.markdown(f"**目前進度：** {session.current_index + 1} / {len(session.question_set)}")
    st.markdown("---")
    st.markdown("### 📊 主題進度概覽")

    current_topic = current_q.get("topic") if current_q else None
    answered_ids = {r["question_id"] for r in session.responses}

    for section, questions in MANUAL_SECTION_QUESTIONS.items():
        filtered_questions = [
            q for q in questions
            if (
                (current_stage == "basic" and q["difficulty"] == STAGE_MAP["basic"] and not q["id"].startswith("C"))
                or (current_stage == "advanced" and q["difficulty"] in [STAGE_MAP["basic"], STAGE_MAP["advanced"]])
            )
        ]

        total = len(filtered_questions)
        answered = sum(1 for q in filtered_questions if q["id"] in answered_ids)
        checked = "✅ " if answered == total else ""
        expanded = section == current_topic

        with st.expander(f"{checked}{section}", expanded=expanded):
            for idx, q in enumerate(filtered_questions, 1):
                is_done = q["id"] in answered_ids
                css_class = "question-item completed" if is_done else "question-item"
                st.markdown(
                    f"<div class=\"{css_class}\" onclick=\"window.location.href='#{q['id']}'\">{idx}. {q['title']}</div>",
                    unsafe_allow_html=True
                )
                if st.session_state.get("jump_to") == q["id"]:
                    index = next((i for i, item in enumerate(session.question_set) if item["id"] == q["id"]), None)
                    if index is not None:
                        session.jump_to(index)
                        st.session_state["jump_to"] = None
                        st.rerun()
                st.markdown(f"<a name='{q['id']}'></a>", unsafe_allow_html=True)

progress = session.get_progress()

if current_q:
    st.markdown(f"#### 🎯 學習主題：<br>{current_q.get('learning_goal', '')}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<h3>{current_q.get('text', '')}</h3>", unsafe_allow_html=True)
    st.markdown(f"**題目說明：** {current_q.get('question_note', '')}")

    options = current_q["options"]
    option_notes = current_q.get("option_notes", {})
    labeled_options = [f"{opt}：{option_notes.get(opt, '')}" for opt in options]

    selected = []
    if current_q["type"] == "single":
        selected_option = st.radio("可選擇：", labeled_options)
        if selected_option:
            selected = [selected_option.split("：")[0]]
    else:
        selected_options = st.multiselect("可複選：", labeled_options)
        selected = [opt.split("：")[0] for opt in selected_options]

    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        user_comment = st.text_input("💬 若有想法或要問 AI，可先輸入再提交：", label_visibility="collapsed")
    with col2:
        if st.button("✅"):
            result = session.submit_response(selected)
            add_context_entry(current_q["id"], selected, current_q["text"])
            save_to_json(session)
            if "error" in result:
                st.error(result["error"])
            else:
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
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