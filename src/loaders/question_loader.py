# 📂 src/loaders/question_loader.py
"""
讀取所有題庫 CSV，並依據 industry_type 整理為 dict 格式。
提供檢查欄位格式一致性的基本功能。
"""

import csv
import os

DATA_FOLDER = "data"
REQUIRED_FIELDS = [
    "question_id",
    "industry_type",
    "question_text",
    "topic_category",
    "difficulty_level",
    "report_section",
    "answer_tags",
    "option_type",
    "allow_custom_answer",
    "allow_skip",
    "free_answer_note"
]

def load_all_question_data(data_folder=DATA_FOLDER):
    """
    讀取指定資料夾中所有題庫 CSV 檔案。
    回傳依照 industry_type 分類的 dict 結構。
    """
    all_questions = {}

    for filename in os.listdir(data_folder):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(data_folder, filename)
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
            if missing:
                raise ValueError(f"❌ 欄位缺失：{filename} 缺少欄位 {missing}")

            rows = list(reader)
            if not rows:
                continue

            industry = rows[0]["industry_type"]
            if industry not in all_questions:
                all_questions[industry] = []

            all_questions[industry].extend(rows)

    return all_questions


if __name__ == "__main__":
    result = load_all_question_data()
    for k, v in result.items():
        print(f"✅ {k} 題數：{len(v)}")
