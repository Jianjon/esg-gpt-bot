# 題庫欄位說明文件（question_schema.md）

本文件定義 ESG GPT 問答系統的題庫格式規範。所有產業題庫請使用 `.csv` 格式，並遵守以下欄位結構。

---

## 📌 必填欄位

| 欄位名稱        | 型別     | 說明 |
|-----------------|----------|------|
| question_id      | string   | 題目唯一代碼（如：C001） |
| industry_type    | string   | 產業名稱（如：餐飲業、旅宿業） |
| question_text    | string   | 題目主文字內容 |
| topic_category   | string   | 主題分類（如：邊界設定與組織資訊、排放源辨識與確認、數據收集方式與能力、內部管理與SOP現況、報告需求與後續行動） |
| option_type      | string   | 題型類型：`single` / `multiple` / `text` |
| difficulty_level | string   | `beginner` / `advanced` |
| question_note    | string   | 題目補充說明（選填，會顯示在題目下方） |

---

## ✅ 選項與解釋（固定五個選項）

| 欄位名稱        | 型別     | 說明 |
|-----------------|----------|------|
| option_A ~ option_E       | string   | 各選項文字 |
| option_A_note ~ option_E_note | string | 各選項的解釋內容，用於教學提示與報告依據 |

---

## 🔄 進階控制欄位（可選）

| 欄位名稱        | 型別     | 說明 |
|-----------------|----------|------|
| follow_up        | string   | 延伸問題建議（可逗號分隔，或用 JSON 陣列） |
| allow_custom_answer | bool  | 是否允許輸入自由答案（true/false） |
| allow_skip       | bool     | 是否允許「不知道」直接跳題（true/false） |
| free_answer_note | string   | 自由回答時顯示提示（如：「請說明現況」） |
| report_topic     | string   | 此題對應報告段落分類（如：排放盤點、教育訓練） |
| learning_goal    | string   | 學習目的／認知重點 |
| answer_tags      | string[] | 此題選項關聯的分析標籤（如：['租賃', '範疇一']）

---

## 📝 建議檔名格式

以產業命名題庫：

```
Question_Retail.csv
Question_Hotel.csv
Question_Logistics.csv
...
```

---

## 🧩 題庫格式注意事項

- 所有選項欄位不可為空
- 所有題目需有 `question_id` 且唯一
- 如需支援多語言，請備份為 `Question_Retail_en.csv` 等版本

---

製作協力：Jon & ChatGPT  
版本：v1.0（2025/04）
