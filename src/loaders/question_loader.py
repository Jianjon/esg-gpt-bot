import pandas as pd
import os

# 題號開頭對應主題分類
MODULE_MAP = {
    "C": "ESG 教學導入（教學前導）",
    "B": "邊界設定與組織資訊",
    "S": "排放源辨識與確認",
    "D": "數據收集方式與能力",
    "M": "內部管理與SOP現況",
    "R": "報告需求與後續行動"
}

# 對應產業題庫檔案名稱
INDUSTRY_FILE_MAP = {
    "餐飲業": "Restaurant.csv",
    "旅宿業": "Hotel.csv",
    "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv",
    "物流業": "Logistics.csv",
    "辦公室服務業": "Offices.csv"
}

# 對應難度階段
STAGE_MAP = {
    "basic": "beginner",
    "advanced": "intermediate"
}

def load_questions(industry: str, stage: str = "basic", skip_common: bool = False) -> list:
    filename = INDUSTRY_FILE_MAP.get(industry)
    if not filename:
        raise ValueError(f"找不到產業對應的題庫：{industry}")

    path = os.path.join("data", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到題庫檔案：{path}")

    df = pd.read_csv(path)

    required_cols = [
        "question_id", "question_text", "difficulty_level", "option_type", "answer_tags"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"題庫缺少必要欄位：{col}")

    if stage not in STAGE_MAP:
        raise ValueError(f"輸入值錯誤：stage 應為 basic 或 advanced，但收到：{stage}")

    mapped_stage = STAGE_MAP[stage]
    df = df[df["difficulty_level"] == mapped_stage]

    questions = []
    for _, row in df.iterrows():
        qid = row["question_id"]

        topic = row.get("topic_category", "").strip()
        if not topic and isinstance(qid, str) and len(qid) > 0:
            prefix = qid[0]
            topic = MODULE_MAP.get(prefix, "未分類")

        options = []
        option_notes = {}
        for opt in ["A", "B", "C", "D", "E"]:
            opt_key = f"option_{opt}"
            note_key = f"option_{opt}_note"
            val = row.get(opt_key)
            if pd.notna(val):
                options.append(val)
                option_notes[val] = row.get(note_key, "")

        question_data = {
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
        }

        questions.append(question_data)

    # ✅ 排除常識題（C000 ~ C099）
    if skip_common:
        questions = [q for q in questions if not (q["id"].startswith("C0"))]

    # ✅ 題號排序，確保 C000~C004 在最前面
    def question_sort_key(q):
        qid = q["id"]
        prefix = qid[0]
        num_part = int(qid[1:]) if qid[1:].isdigit() else 999
        return (prefix, num_part)

    questions.sort(key=question_sort_key)

    return questions
