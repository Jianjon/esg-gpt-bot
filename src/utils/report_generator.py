# 📂 src/generators/report_generator.py

"""
報告產生器：依據使用者作答內容，從語句模組與向量段落產出報告草稿。
支援初階報告生成（依題目分區，聚合句子＋RAG 段落）
"""

from typing import List, Dict
from loaders.question_loader import load_all_question_data
from loaders.template_loader import load_all_templates
from src.utils.context_loader import load_user_session
from src.utils.report_utils import generate_user_background_section
from src.utils.rag_retriever import RAGRetriever


def generate_basic_report(
    user_answers: List[Dict],
    question_data: Dict,
    templates: Dict,
    user_info: Dict = None,
    use_rag: bool = True,
    rag_folder: str = "ISO 14064-1"  # 預設使用的向量資料夾
) -> str:
    """
    產生初階報告（草稿），依據使用者問卷回答 + RAG 補充內容。

    Args:
        user_answers: 問卷回答列表（含 question_id, selected_option）
        question_data: 全部題目原始資料
        templates: 全部語句模板
        user_info: 使用者基本資料（含前導問卷）
        use_rag: 是否補充 RAG 段落
        rag_folder: RAG 向量庫子資料夾（預設為 ISO 14064-1）

    Returns:
        report_text (str): 報告草稿內容
    """
    report_sections = {}
    retriever = RAGRetriever()
    question_map = {q["question_id"]: q for questions in question_data.values() for q in questions}

    for ans in user_answers:
        qid = ans["question_id"]
        question = question_map.get(qid)
        if not question:
            continue

        section = question.get("report_section", "其他說明")
        industry = question.get("industry_type", "通用")
        question_text = question.get("question_text", "")

        # 加入語句模板
        sentence_pool = templates.get(industry, {}).get(section, [])
        selected_sentence = sentence_pool[0] if sentence_pool else "（尚無語句模板）"

        if section not in report_sections:
            report_sections[section] = []
        report_sections[section].append(f"- {selected_sentence}")

        # 加入向量段落
        if use_rag:
            try:
                chunks = retriever.search_chunks(query=question_text, doc_folder=rag_folder, top_k=2)
                for chunk in chunks:
                    report_sections[section].append(f"> {chunk['text']}")
            except Exception as e:
                report_sections[section].append(f"> ⚠️ 向量補充失敗：{e}")

    # 組合報告內容
    report_text = ""

    # 使用者背景摘要
    if user_info and "user_intro_survey" in user_info:
        report_text += generate_user_background_section(user_info["user_intro_survey"])
        report_text += "\n\n---\n\n"

    for section, lines in report_sections.items():
        report_text += f"### {section}\n"
        report_text += "\n".join(lines) + "\n\n"

    return report_text.strip()


# ✅ 本地測試用
if __name__ == "__main__":
    questions = load_all_question_data()
    templates = load_all_templates()
    answers = [
        {"question_id": "C001", "selected_option": "A"},
        {"question_id": "C004", "selected_option": "B"},
        {"question_id": "C010", "selected_option": "D"},
    ]
    user = load_user_session("綠意餐飲", "Jon")

    report = generate_basic_report(answers, questions, templates, user)
    print("📝 報告產出如下：\n")
    print(report)
