# 📂 src/generators/report_generator.py
"""
報告產生器：依據使用者作答內容，從語句模組中擷取對應語句，產出初步報告草稿。
目前支援產出初階報告（依照每題 report_section 分組，聚合句子）
"""

from loaders.question_loader import load_all_question_data
from loaders.template_loader import load_all_templates


def generate_basic_report(user_answers, question_data, templates):
    """
    user_answers: List[Dict]，包含使用者回答的題目 ID 及其選項，例如：
      [{"question_id": "C001", "selected_option": "A"}, ...]

    question_data: Dict[str, List[Dict]]，由 question_loader 提供
    templates: Dict[str, Dict[str, List[str]]]，由 template_loader 提供

    回傳一段報告文字（string）
    """
    report_sections = {}

    # 建立查表：快速從 question_id 找到對應題目資料
    question_map = {q["question_id"]: q for questions in question_data.values() for q in questions}

    for ans in user_answers:
        qid = ans["question_id"]
        question = question_map.get(qid)
        if not question:
            continue

        industry = question["industry_type"]
        section = question["report_section"]

        sentence_pool = templates.get(industry, {}).get(section, [])
        if not sentence_pool:
            continue

        # 簡化版本：隨機抽一句，未來可依 tags 或其他機制篩選
        selected_sentence = sentence_pool[0]

        if section not in report_sections:
            report_sections[section] = []

        report_sections[section].append(selected_sentence)

    # 彙整報告文字
    report_text = ""
    for section, lines in report_sections.items():
        report_text += f"\n\n### {section}\n"
        for line in lines:
            report_text += f"- {line}\n"

    return report_text.strip()


if __name__ == "__main__":
    # 測試用：讀取資料與語句
    questions = load_all_question_data()
    templates = load_all_templates()

    sample_answers = [
        {"question_id": "C001", "selected_option": "A"},
        {"question_id": "C004", "selected_option": "B"},
        {"question_id": "C010", "selected_option": "D"},
    ]

    report = generate_basic_report(sample_answers, questions, templates)
    print("\n📝 初階報告草稿：")
    print(report)
