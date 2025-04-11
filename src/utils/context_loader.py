from pathlib import Path
import json

def load_user_session(company: str, name: str) -> dict:
    """
    從 data/sessions/{company}_{name}.json 讀取使用者資料
    """
    path = Path("data/sessions") / company / f"{name}.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}
