
# 模組設計規劃書 module_plan_v2.txt

本文件為 ESG 教學問答系統之技術模組說明，說明每個模組的責任、功能範圍、參數傳遞、支援的前端元件與與其他模組之間的依賴關係。目標為「清楚、穩定、可維護、可擴充」的模組架構。

---

## 【1】question_loader.py

- 功能：載入指定產業的題庫檔（CSV），並轉為可供程式操作的資料結構
- 輸入參數：
  - `industry_code`（str）：產業代碼（如 "retail", "logistics"）
- 輸出資料：
  - List of dicts，每題內容包含題號、章節、題目文字、選項、說明、followup、level等
- UI/前端支援：
  - 啟動初始畫面時自動綁定題庫
- 依賴模組：
  - `topic_manager.py`（取得題庫路徑）
- 邊界定義：
  - 不處理資料顯示或進度控制，只做題庫載入與轉換

---

## 【2】flow_controller.py

- 功能：控制問答進行的流程，包含階段切換（初階/進階）、跳題控制、是否允許修改
- 輸入參數：
  - `user_state`（dict）：用戶目前進度、階段、是否為第一次填答
- 輸出資料：
  - 下一題題目 / 作答完成通知 / 鎖定提示
- UI/前端支援：
  - 左側進度條控制
  - 提示「是否進入進階」、「是否重作」
- 依賴模組：
  - `answer_saver.py`、`question_loader.py`
- 邊界定義：
  - 不產出題目內容，不儲存答案

---

## 【3】answer_saver.py

- 功能：記錄使用者每題回答與版本歷程
- 輸入參數：
  - `question_id`（str/int）
  - `answer`（str / JSON）
  - `user_id`（可選）
- 輸出資料：
  - 寫入 JSON / SQLite 資料（可版本對照）
- UI/前端支援：
  - 回答確認動畫
  - 顯示「V1」、「V2」等版本切換標記
- 依賴模組：
  - 可與 `version_comparator.py` 串聯
- 邊界定義：
  - 不評分、不解釋、不判斷正確性

---

## 【4】followup_engine.py

- 功能：根據使用者回答內容，提供延伸提問建議（灰色泡泡形式）
- 輸入參數：
  - `question_id`、`user_answer`
- 輸出資料：
  - 建議提問語句（list of strings）
- UI/前端支援：
  - 顯示在 AI 對話泡泡下方、灰色提示文字
- 依賴模組：
  - `question_loader.py` 提供 followup 欄位
- 邊界定義：
  - 不處理自由問答回應，僅提示引導式提問

---

## 【5】response_engine.py

- 功能：針對使用者輸入的自由問答，產出對應的 GPT 回覆
- 輸入參數：
  - `user_input`（str）
  - `context`（回答上下文、產業題庫）
- 輸出資料：
  - GPT 回應文字 + 可選解析段落
- UI/前端支援：
  - 對話泡泡（右側）、可擴充顯示（卡片式）
- 邊界定義：
  - 不處理回答儲存或流程控制

---

## 【6】report_generator.py

- 功能：根據使用者作答內容，產出摘要報告（初階/進階）
- 輸入參數：
  - `answers`（list of dict）
  - `version_id`（str）
- 輸出資料：
  - 文字報告（500字或1000字），段落結構
- UI/前端支援：
  - 顯示報告段落 + 強調關鍵字
- 依賴模組：
  - `answer_saver.py` 提供完整紀錄
- 邊界定義：
  - 不存檔、不列印、不轉檔（這些留給報告輸出模組）

---

## 【7】ui_state_manager.py

- 功能：管理所有前端狀態顯示與切換，包括：
  - 問題欄是否鎖定
  - 選項顯示與說明格式
  - 自由輸入欄切換狀態
- UI/前端支援：
  - 固定題目區塊
  - 灰色引導問題（來自 followup_engine）
  - 泡泡交錯對話區
- 依賴模組：
  - flow_controller, response_engine, followup_engine

---

## 【8】topic_manager.py

- 功能：管理題庫來源、題庫版本、對應產業
- 功能點：
  - 掃描 `/data/` 內題庫
  - 顯示可選擇的產業清單
  - 提供題庫語系、版本資訊
- UI/前端支援：
  - 題庫選單下拉欄
  - 載入動畫
- 邊界定義：
  - 不儲存答案、不顯示內容

---

## 【9】illustration_helper.py（擬新增）

- 功能：根據章節顯示圖解說明（小圖卡、繪本式介面）
- 輸入參數：
  - `section_id` 或 `question_id`
- 輸出資料：
  - 圖片名稱、對應說明
- UI/前端支援：
  - 插畫區塊與說明區交錯出現
- 備註：
  - 可搭配固定幾張 ESG 插圖庫做引導

---

## 模組關係圖（文字版）

1. 使用者選擇產業 → `topic_manager` → `question_loader`
2. 問題送出後 → `flow_controller` → 控制跳題與階段
3. 回答送出 → `answer_saver` 記錄 → 呼叫 `followup_engine` 顯示建議問題
4. 使用者自由輸入 → `response_engine` 回應
5. 全部完成 → `report_generator` 產出摘要 → UI 顯示報告卡
6. 所有顯示互動 → `ui_state_manager` 控制狀態變化

---

【版本】module_plan v2.0
【建立者】使用者 x ChatGPT 協作規劃
