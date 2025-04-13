# src/utils/sidebar_labeler.py

import os
import json
import pandas as pd
from typing import Dict
from src.utils.gpt_tools import call_gpt

INDUSTRY_FILE_MAP = {
    "餐飲業": "Restaurant.csv",
    "旅宿業": "Hotel.csv",
    "零售業": "Retail.csv",
    "小型製造業": "SmallManufacturing.csv",
    "物流業": "Logistics.csv",
    "辦公室服務業": "Offices.csv"
}

def generate_sidebar_labels_for_industry(industry: str, stage: str = "basic", data_dir="data", save_dir="data/labels") -> Dict[str, str]:
    """
    為指定產業與階段（basic / advanced）產生側邊欄題目簡化標籤，並儲存成 JSON。
    回傳格式：{question_id: label}
    """

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    filename = INDUSTRY_FILE_MAP.get(industry)
    if not filename:
        raise ValueError(f"❌ 找不到產業對應的檔案：{industry}")

    path = os.path.join(data_dir, filename)
    df = pd.read_csv(path)

    # 根據階段篩選題目
    if stage == "basic":
        df = df[df["difficulty_level"] == "beginner"]
    elif stage == "advanced":
        df = df[df["difficulty_level"].isin(["beginner", "intermediate"])]
    else:
        raise ValueError("❌ 無效的階段參數，請使用 'basic' 或 'advanced'")

    if df.empty:
        raise ValueError("⚠️ 無符合條件的題目可用於簡化")

    prompt_list = [f"{i+1}. {row['question_text']}" for i, row in df.iterrows()]
    combined_prompt = "\n".join(prompt_list)

    prompt = f"""
你是一位協助設計 ESG 問卷的顧問。
請將每一題簡化為 6～8 字的「側邊欄顯示用標籤」。
請保留題號順序，輸出 JSON 格式：key 為原始題目（question_text），value 為簡化標籤。

{combined_prompt}
    """

    # --- 呼叫 GPT 產生對應標籤 ---
    result = call_gpt(prompt, model="gpt-4")
    try:
        text_to_label = json.loads(result)
    except Exception as e:
        raise ValueError(f"⚠️ GPT 回傳無法轉換為 JSON：{e}\n原始內容：\n{result}")

    # --- 轉換為 {question_id: label} 格式 ---
    id_to_label = {}
    for _, row in df.iterrows():
        qid = row["question_id"]
        qtext = row["question_text"]
        label = text_to_label.get(qtext)
        if label:
            id_to_label[qid] = label
        else:
            id_to_label[qid] = qtext[:12]  # fallback

    # --- 儲存標籤檔案 ---
    out_name = f"sidebar_labels_{industry}_{stage}.json"
    out_path = os.path.join(save_dir, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(id_to_label, f, ensure_ascii=False, indent=2)

    return id_to_label
