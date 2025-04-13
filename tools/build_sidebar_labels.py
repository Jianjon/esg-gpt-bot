import os
import pandas as pd
import json
from src.utils.sidebar_labeler import generate_sidebar_label  # ✅ 這是呼叫 GPT 產生題目簡化標籤的函式

INDUSTRY_FILE_MAP = {
    "旅宿業": "Hotel.csv",
    "餐飲業": "Restaurant.csv",
    "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv",
    "物流業": "Logistics.csv",
    "辦公室服務業": "Offices.csv",
}

DATA_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_DIR, "sidebar_labels")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_sidebar_labels_for_all_industries():
    for industry_name, file_name in INDUSTRY_FILE_MAP.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            print(f"⚠️ 找不到檔案：{file_path}")
            continue

        df = pd.read_csv(file_path)
        label_map = {}

        for _, row in df.iterrows():
            qid = row["question_id"]
            text = str(row.get("question_text", "")).strip()
            difficulty = row.get("difficulty_level", "beginner")

            if not text:
                continue

            try:
                label = generate_sidebar_label(text)
                label_map[qid] = {
                    "label": label,
                    "difficulty": difficulty
                }
            except Exception as e:
                label_map[qid] = {
                    "label": f"（標籤失敗）{e}",
                    "difficulty": difficulty
                }

        output_path = os.path.join(OUTPUT_DIR, f"sidebar_labels_{industry_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(label_map, f, ensure_ascii=False, indent=2)
        print(f"✅ 已儲存：{output_path}")

if __name__ == "__main__":
    build_sidebar_labels_for_all_industries()
