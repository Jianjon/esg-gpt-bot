import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from sessions.answer_session import AnswerSession


# ========= 路徑處理 =========

def get_json_path(user_id: str) -> str:
    os.makedirs("data/responses", exist_ok=True)
    return f"data/responses/{user_id}.json"


def get_sqlite_path() -> str:
    os.makedirs("data/sqlite", exist_ok=True)
    return "data/sqlite/sessions.db"


# ========= JSON 儲存與載入 =========

def save_to_json(session: AnswerSession) -> None:
    """將作答紀錄儲存為 JSON"""
    path = get_json_path(session.user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.get_summary(), f, ensure_ascii=False, indent=2)


def load_from_json(user_id: str, question_set: list) -> Optional[AnswerSession]:
    """從 JSON 還原作答紀錄，若無檔案則回傳 None"""
    path = get_json_path(user_id)
    if os.path.exists(path):
        with path.open("r", encoding="utf-8") as f:
          data = json.load(f)
        return AnswerSession.from_dict(data, question_set)
    return None


# ========= SQLite 儲存 =========

def save_to_sqlite(session: AnswerSession) -> None:
    """將作答紀錄儲存至 SQLite（可供後續查詢與分析）"""
    db_path = get_sqlite_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 建立資料表
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

    # 寫入每筆回覆
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

def get_json_path(user_id: str) -> Path:
    path = Path("data/responses")
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{user_id}.json"