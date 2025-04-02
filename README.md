
# ESG GPT 問答教學系統

這是一套以 ESG（環境、社會、治理）與溫室氣體盤查為核心主題的教學型問答系統。透過題庫驅動、AI 回應、報告生成與互動式對話，讓使用者一步步學習並回應企業永續實務挑戰。

---

## 🔧 系統特色

- 教學導向問答：以 CSV 題庫為基礎，支援初階與進階學習
- 分段互動流程：使用者依序作答、無法跳題，避免碎片學習
- AI 輔助學習：提供延伸提問與自然語言回饋
- RAG 模式預備：支援接入企業文件、法規知識庫進行回應
- 報告生成：依據作答紀錄產出 500 / 1000 字摘要診斷
- 完整模組化設計：所有功能皆可擴充、替換、重用

---

## 📁 專案目錄結構

```
esg-gpt-bot/
├── main.py
├── config.yaml
│
├── modules/
│   ├── question_loader.py
│   ├── flow_controller.py
│   ├── answer_saver.py
│   ├── followup_engine.py
│   ├── response_engine.py
│   ├── report_generator.py
│   ├── ui_state_manager.py
│   ├── topic_manager.py
│   ├── illustration_helper.py
│   ├── rag_engine.py
│   ├── embedding_indexer.py
│   └── version_comparator.py
│
├── data/                         # 題庫資料夾
│   ├── questions_retail.csv
│   ├── ...
│
├── knowledge_vector_db/         # 向量資料庫儲存區
├── notes/                       # 系統說明與規劃文件
│   ├── system_flow_plan.txt
│   └── module_plan_v2.txt
└── README.md
```

---

## ✅ 模組功能總覽

| 模組名稱 | 功能說明 |
|----------|----------|
| `question_loader.py` | 載入產業題庫，標記章節與階段 |
| `flow_controller.py` | 控制進度、題目順序與進階切換 |
| `answer_saver.py` | 儲存與版本化使用者回答 |
| `followup_engine.py` | 生成延伸提問建議（引導泡泡） |
| `response_engine.py` | 回應使用者自由提問（含 RAG 模式） |
| `report_generator.py` | 產出初階/進階報告摘要 |
| `ui_state_manager.py` | 控制畫面區塊狀態與進度條顯示 |
| `topic_manager.py` | 管理題庫載入與切換 |
| `illustration_helper.py` | 插入圖解說明或繪本式提示 |
| `rag_engine.py` | 從向量庫中檢索補充資料 |
| `embedding_indexer.py` | 建立向量資料庫（支援 PDF / txt） |
| `version_comparator.py` | 分析使用者不同版本回答差異（可選） |

---

## 🧠 使用 GPT 模型的方式

- 回答回饋、自由提問：由 `response_engine.py` 呼叫 GPT-3.5 / GPT-4
- 若啟用 RAG，則從 `rag_engine.py` 抽取補充資料再組合 prompt

---

# ESG 題庫管理系統

本專案整理並管理六大產業的 ESG 教學與診斷題庫，包含：

- 餐飲業（Restaurant）
- 旅宿業（Hotel）
- 零售業（Retail）
- 小型製造業（SmallManufacturing）
- 物流業（Logistics）
- 辦公室與服務業（Offices）

## 檔案結構說明

- `data/`：各產業題庫資料，格式為 CSV。
- `schema/question_schema.md`：欄位說明與設計規則。
- `demo/demo_questions.csv`：展示題型格式範例。


## 📈 報告產出方式

- 初階報告：回答滿 25 題，自動產出 500 字摘要
- 進階報告：回答完 30–35 題，產出約 1000 字完整診斷
- 支援版本對照與建議段落提示（未來支援 Markdown/PDF 匯出）

---

## 🌱 擴充建議

你可以進一步加入：

- 資料視覺化模組（chart_generator.py）
- 多語系切換（i18n_translator.py）
- Google Sheets 自動填答紀錄上傳
- 後台資料審閱與報告審核模組

---

## 🧭 開發理念

本專案強調：
- **清晰結構：** 每個模組職責明確，不混用功能
- **擴充彈性：** 題庫與模型分離，可隨時換資料或升級 AI
- **使用者體驗：** 導向式學習，具備人性化引導
- **永續價值：** 教學與診斷並重，不只是一個問卷系統

---

## Canvas 系統設計

可參考 `/canvas/` 資料夾，包含完整系統規劃圖（模組邏輯、AI 角色、資料結構）。

---
# 📁 Canvas 文件總覽（ESG 顧問互動系統設計圖）

本資料夾為本系統設計的 Canvas 文件集，目的在於清楚釐清系統模組、使用者流程、資料欄位邏輯與 AI 參與角色，便於開發、設計與後續維護協作。

---

## 📚 Canvas 清單

| Canvas 編號 | 檔名                            | 說明                                                                 |
|--------------|----------------------------------|----------------------------------------------------------------------|
| L1           | `canvas_l1_system_overview.md`   | 系統模組總覽圖，說明所有核心功能模組與邏輯流程                                     |
| L2           | `canvas_l2_user_flow.md`         | 使用者互動流程圖，從進入系統 → 選擇題庫 → 作答 → 產出報告的全流程拆解                     |
| L3           | `canvas_l3_question_data_mapping.md` | 題庫欄位對應圖，說明每一個欄位的作用位置（UI 顯示、AI 使用、報告輸出）                  |
| L4           | `canvas_l4ai_support.md`         | AI 參與模組設計圖，標示 AI 如何支援教學補充、報告生成、自由回答理解與標籤分類等任務             |

---

## 📌 預計新增（未來）

| Canvas 編號 | 預定名稱（草稿）       | 預期內容描述                                                                 |
|--------------|------------------------|------------------------------------------------------------------------------|
| L5           | `canvas_l5_report_logic.md` | 報告組段邏輯設計圖，對應題目 → 段落 → 建議內容產出（含標籤與分類），便於後續報告模組實作       |
| L6           | `canvas_l6_rag_architecture.md` | 知識擴充架構設計（RAG），規劃如何整合 FAQ、白皮書、產業資料等做自由問答與補強報告寫作用途      |

---

## ✨ 本文件由 Jon 與 AI 協作製作

透過 GPT 模型輔助思考與設計，並配合 Markdown 文件管理與 GitHub 協作儲存，打造出高度模組化、可維護、可擴展的 ESG 顧問互動系統。

---

如需貢獻其他 Canvas 或修訂，請建立 `canvas_lX_xxx.md` 命名格式，並於本文件中登錄說明 ✍️


【製作協作】Jon x ChatGPT | v1.0 完整模組設計 | 2024–2025
