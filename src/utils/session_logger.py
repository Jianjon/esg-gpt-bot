import os
import json
from datetime import datetime
from typing import List, Dict


LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_log_path(user_id: str) -> str:
    """取得使用者操作紀錄的檔案路徑"""
    return os.path.join(LOG_DIR, f"{user_id}_log.json")


def log_action(user_id: str, action: str, metadata: Dict = None) -> None:
    """記錄一個使用者動作（可附加任意 metadata）"""
    log_path = get_log_path(user_id)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "metadata": metadata or {}
    }

    logs = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)

    logs.append(log_entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_logs(user_id: str) -> List[Dict]:
    """讀取某使用者的所有操作紀錄"""
    log_path = get_log_path(user_id)
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_logs(user_id: str) -> None:
    """清除某使用者的所有操作紀錄"""
    log_path = get_log_path(user_id)
    if os.path.exists(log_path):
        os.remove(log_path)
