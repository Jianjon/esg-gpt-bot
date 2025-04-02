# ✅ ESG 顧問系統欄位與參數定義總表

本文件作為系統開發與報告模組撰寫時的欄位參考依據，確保所有資料一致、可追蹤、便於後續維護與擴充。

---

## ✅ 第一點：參數名稱與欄位格式 必須一致

這樣可以保證：
- 報告產生器能正常讀取所有題目資料；
- 每個語句模組都能正確比對；
- 未來擴充產業、題庫、模型時不需要大改程式。

---

## 📋 所有診斷模組使用到的欄位定義表

| 欄位名稱             | 用途說明                                     | 是否必要 | 資料格式         |
|----------------------|----------------------------------------------|----------|------------------|
| question_id          | 題號（如：C001、S003）                       | ✅       | `string`         |
| industry_type        | 產業分類（如：零售業、飯店業）               | ✅       | `string`         |
| question_text        | 題目內容（用戶看到的文字）                   | ✅       | `string`         |
| topic_category       | 主題分類（如：數據收集方式與能力）           | ✅       | `string`         |
| difficulty_level     | 難度等級，目前統一為 beginner                | ✅       | `string (enum)`  |
| report_section       | 對應報告段落（邊源算報查五選一）             | ✅       | `string (enum)`  |
| learning_objective   | 題目的學習目的說明                           | ⬜       | `string`         |
| answer_tags          | 題目中提及的關鍵詞（可幫助報告生成）         | ✅       | `string[]` 陣列  |
| option_type          | 題型：multiple / multi_learning 等           | ✅       | `string (enum)`  |
| allow_custom_answer  | 是否允許自由作答                             | ✅       | `bool`           |
| allow_skip           | 是否允許跳題                                 | ✅       | `bool`           |
| free_answer_note     | 自由作答的提示訊息（如「請補充說明」）       | ✅       | `string`         |

---

## 📁 建議這些欄位應同時出現在：

- 題庫 `.csv` 檔中（每題一行）
- 模組 `.md` 標頭段（或轉為 YAML block）
- 程式中用於產出報告的中介格式（如 `answer_json` 或 `question_object`）

---

✅ 本表定義為固定參考，不建議日後再任意增刪欄位。如需增修，請另開 `schema_change_log.md` 留存變更紀錄。
