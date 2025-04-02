# 🌱 ESG GPT 問答診斷系統：淨零小幫手（ESG Service Path）

這是一套結合 ESG 題庫、AI 回饋、診斷報告與本地知識問答（RAG 模式）的完整 ESG 教學系統，支援六大產業、初階與進階診斷、進度追蹤與企業化管理。

---

## 🧩 系統架構功能總覽

| 類別 | 功能說明 |
|------|---------|
| 🎓 問卷系統 | 六大產業題庫（初階 + 進階），分段作答、不跳題，記錄進度 |
| 🤖 AI 回饋 | GPT 自動產生診斷建議與報告內容（可選用 RAG 模式強化） |
| 📈 分析報告 | 500 / 1000 字診斷摘要、自動比對 baseline，支援 PDF 擴充 |
| 💬 RAG 模組 | 支援載入 PDF / txt 轉為向量庫，提供問答補充資訊 |
| 🗃️ 作答儲存 | JSON / SQLite 儲存作答進度與內容，可接續、匯出分析 |
| 👤 使用者管理 | Welcome 頁面輸入姓名 / 公司 / 產業，自動載入對應題庫 |

---

## 📁 目錄結構概覽

```
esg-gpt-bot/
├── data/                   # 題庫、baseline、向量庫、作答紀錄
│   ├── Restaurant.csv
│   ├── baselines/
│   ├── responses/         # JSON
│   ├── sqlite/            # SQLite DB
│   ├── docs/              # 用於 RAG 的知識文件
│   └── vector_store/      # FAISS 向量儲存
│
├── src/
│   ├── app.py             # 主診斷問卷頁
│   ├── welcome.py         # 使用者輸入頁面
│   ├── sessions/          # answer_session.py（問卷狀態）
│   ├── managers/          # baseline, feedback, report 模組
│   ├── loaders/           # 題庫、文件、報告模版載入
│   └── retriever/         # 向量庫模組（loader, vector_store, query_engine）
│
├── .env                   # OpenAI API key 設定
├── requirements.txt       # 相依套件（含 Streamlit, LangChain）
└── README.md
```

---

## ✅ 如何使用

### 📦 安裝必要套件
```bash
pip install -r requirements.txt
```

### 🚀 啟動系統入口（建議從 welcome 開始）
```bash
streamlit run src/welcome.py
```

填寫姓名、公司、產業後進入診斷頁面。

---

## 🧠 技術與模組總覽

| 模組 | 功能 |
|------|------|
| `answer_session.py` | 控制作答流程、記錄問卷回覆、進度追蹤 |
| `question_loader.py`| 讀取題庫（依產業、階段分類） |
| `baseline_manager.py`| 匯入公司 baseline 進行比對 |
| `report_manager.py` | 生成診斷報告文字（可接 PDF） |
| `feedback_manager.py`| 使用 GPT 生成題目回饋與總體分析 |
| `session_logger.py` | 將作答內容儲存至 JSON / SQLite |
| `template_loader.py` | 讀取報告句子樣板（可分類產業/主題） |
| `vector_store.py` | 建立/讀取 FAISS 本地向量庫 |
| `query_engine.py` | 啟動向量檢索 + GPT 回答查詢 |
| `loader.py` | 載入 PDF / txt 並分段 |

---

## 🔜 未來可擴充項目（你也可以貢獻！）
- 🔒 使用者登入與權限管理
- 📄 診斷報告 PDF 輸出
- 📊 企業問卷歷程統計視覺化
- 📚 多語系題庫（EN / ZH）與 ISO 自動對應

---

如需協作、改進說明或客製化需求，歡迎發 PR 或留言 🙌

