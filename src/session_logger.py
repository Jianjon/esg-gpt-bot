import os
import json
import sqlite3
from datetime import datetime

def get_json_path(user_id):
    os.makedirs("data/responses", exist_ok=True)
    return f"data/responses/{user_id}.json"

def save_to_json(session):
    path = get_json_path(session.user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.get_summary(), f, ensure_ascii=False, indent=2)

def load_from_json(user_id, question_set):
    path = get_json_path(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        from sessions.answer_session import AnswerSession
        session = AnswerSession(user_id=user_id, question_set=question_set, stage=data.get("stage", "basic"))
        session.responses = data.get("responses", [])
        session.current_index = len(session.responses)
        return session
    return None

def save_to_sqlite(session):
    os.makedirs("data/sqlite", exist_ok=True)
    conn = sqlite3.connect("data/sqlite/sessions.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            user_id TEXT,
            question_id TEXT,
            response TEXT,
            topic TEXT,
            question_type TEXT,
            timestamp TEXT
        )
    """)
    now = datetime.now().isoformat()
    for r in session.responses:
        c.execute("""
            INSERT INTO responses (user_id, question_id, response, topic, question_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.user_id,
            r["question_id"],
            json.dumps(r["user_response"], ensure_ascii=False),
            r.get("topic", "未分類"),
            r.get("question_type", "unknown"),
            now
        ))
    conn.commit()
    conn.close()

# 可擴充更多欄位與回報架構
