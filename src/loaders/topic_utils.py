import json
from functools import lru_cache
import os

TOPIC_PATH = os.path.join("data", "topic_structure.json")

@lru_cache(maxsize=1)
def load_topic_structure():
    with open(TOPIC_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_topic_and_title_by_id(question_id):
    """
    回傳 (主題名稱, 題目簡化標題)
    若找不到則回傳 ("未知主題", question_id)
    """
    topic_data = load_topic_structure()
    for topic, questions in topic_data.items():
        for q in questions:
            if q["id"] == question_id:
                return topic, q["title"]
    return "未知主題", question_id
