
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

## 📚 題庫格式規範

放置於 `data/`，格式為 `.csv`，需包含欄位：

```
id, section, text, options, explanation, followups, level, industry_tag
```

---

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

【製作協作】Jon x ChatGPT | v1.0 完整模組設計 | 2024–2025
