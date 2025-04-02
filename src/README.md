### ✅ 系統程式模組設計（v1 版）
以下是基於目前你的專案架構與 Canvas 設計圖（L1–L6）推導出來的初始六個主要模組，每一個都獨立、清楚、可維護。

📁 /src/loaders/question_loader.py
功能：

- 讀取 /data/ 內所有產業 .csv 題庫檔案

- 檢查欄位一致性（依據 schema）

- 回傳以 industry_type 為 key 的題庫 dict

📁 /src/parsers/answer_parser.py
功能：

- 將使用者答題紀錄（JSON）轉為結構化格式

- 抽取每題的：question_id, report_section, answer_tags

- 對應語句模組時使用

📁 /src/generators/report_generator.py
功能：

- 根據回答結果中的 industry_type + report_section + answer_tags

- 去 /templates/report_sentences/ 找對應內容

- 自動組合為：

   - 初階小段落報告（每 5 題）

   - 全題完成後的完整報告（約 500 字）

📁 /src/renderers/output_formatter.py
功能：

- 將報告輸出為純文字、HTML 或 Markdown

- 加上段落標題、標籤註記與報告時間戳

📁 /src/utils/validation.py
功能：

- 驗證題庫欄位是否符合 /schema/diagnostic_fields.md

- 檢查每題是否有對應語句模組（避免漏段落）

📁 /src/ui/cli_runner.py
功能：

- 提供 CLI 模式跑完整流程（可選題 → 生成報告）

- 模擬日後網頁或 API 接入的操作流程



### 🔁 資料流流程（Summary）

.csv 題庫
   ↓ (question_loader)
使用者答題 JSON
   ↓ (answer_parser)
結構化回答 + 標籤
   ↓ (report_generator)
語句模組 Markdown
   ↓ (output_formatter)
→ 文字報告 / Markdown / HTML

---

### 🧩 程式模組說明（/src）

本系統核心邏輯拆分為六個明確模組，便於維護、測試與擴充：

| 檔案路徑                                | 模組功能說明                                                                 |
|-----------------------------------------|------------------------------------------------------------------------------|
| `/src/loaders/question_loader.py`       | 讀取六個產業題庫 `.csv`，依產業整理為 dict，並驗證欄位一致性。               |
| `/src/parsers/answer_parser.py`         | 將使用者作答結果轉為標準結構，擷取 `report_section` 與 `answer_tags`。     |
| `/src/generators/report_generator.py`   | 根據回答結果與語句模組，自動生成段落式 ESG 簡報。                           |
| `/src/renderers/output_formatter.py`    | 將報告格式化輸出為純文字、Markdown 或 HTML，加入段落與標籤註記。           |
| `/src/utils/validation.py`              | 驗證題庫欄位是否符合 `/schema/diagnostic_fields.md` 規則。                  |
| `/src/ui/cli_runner.py`                 | 命令列工具，模擬完整答題與報告產出流程，方便測試與日後 API 接入前導流程。 |

所有模組設計皆符合「簡化、可維護、可擴充」原則，後續可無痛新增產業、語句模組或模型版本。
