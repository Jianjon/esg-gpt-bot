import pandas as pd
import os

MODULE_MAP = {
    "C": "排放源辨識與確認",
    "S": "排放源辨識與確認",
    "B": "邊界設定與組織資訊",
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

def load_questions(industry: str, stage: str = "basic") -> list:
    filename = INDUSTRY_FILE_MAP.get(industry)
    if not filename:
        raise ValueError(f"找不到產業對應的題庫：{industry}")

    path = os.path.join("data", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到題庫檔案：{path}")

    df = pd.read_csv(path)

    # 標準欄位校驗（部分欄位可選擇性存在）
    required_cols = [
        "question_id", "question_text", "difficulty_level", "option_type", "answer_tags"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"題庫缺少必要欄位：{col}")

    df = df[df["difficulty_level"] == stage]

    questions = []
    for _, row in df.iterrows():
        qid = row["question_id"]
        prefix = qid[0] if isinstance(qid, str) else ""
        topic = row.get("topic_category") or MODULE_MAP.get(prefix, "未分類")
        options = row["answer_tags"].split("|") if isinstance(row["answer_tags"], str) else []

        question_data = {
            "id": qid,
            "industry": row.get("industry_type", industry),
            "text": row.get("question_text", "未填題目內容"),
            "options": options,
            "type": row.get("option_type", "single"),
            "topic": topic,
            "difficulty": row.get("difficulty_level", stage),
            "report_section": row.get("report_section", ""),
            "tags": row.get("answer_tags", "").split("|") if isinstance(row.get("answer_tags"), str) else [],
            "allow_custom_answer": row.get("allow_custom_answer", False),
            "allow_skip": row.get("allow_skip", False),
            "note": row.get("free_answer_note", "")
        }

        questions.append(question_data)

    return questions
