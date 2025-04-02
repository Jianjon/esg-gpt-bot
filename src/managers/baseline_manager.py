# managers/baseline_manager.py

import json
import os

class BaselineManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.baseline = self._load_baseline()

    def _load_baseline(self):
        if not os.path.exists(self.filepath):
            print(f"找不到 baseline，將建立新的：{self.filepath}")
            return {}
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_baseline(self, baseline_dict: dict):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(baseline_dict, f, ensure_ascii=False, indent=2)
        self.baseline = baseline_dict

    def get_baseline(self):
        return self.baseline

    def get_baseline_for_question(self, question_id):
        return self.baseline.get(str(question_id), None)
