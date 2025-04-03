
## ✅ 請建立或更新：`README.md`

```markdown
# ESG GPT 顧問系統 🧠🌱

企業永續 × AI 問答引導 × 碳盤查教學模組  
本專案為一套專為中小企業設計的 ESG 顧問互動平台，提供分產業的教學問卷、自由提問、報告生成與向量資料庫查詢功能。

---

## 🚀 專案特色

- ✏️ ESG 教學式問答系統（分階段互動）
- 🧩 客製化題庫（餐飲、旅宿、零售等 6 大產業）
- 🧠 顧問對談介面（使用 GPT-4o）
- 📚 向量查詢整合 RAG 架構（支援 PDF 知識查詢）
- 📊 自動生成簡易 ESG 回饋摘要報告
- 🧵 Session 作答與回顧追蹤
- 🔧 模組化設計，支援擴充與維護

---

## 📁 專案結構說明

```bash
esg-gpt-bot/
│
├── app.py                     # Streamlit 啟動主介面
├── build_vector_db.py         # 向量庫建置腳本
├── requirements.txt           # 套件安裝清單
│
├── src/                       # 主系統模組
│   ├── consult_chat_app.py      # 顧問對談模式（主頁）
│   ├── welcome.py               # 使用者姓名/產業輸入頁
│   ├── context_tracker.py       # 作答內容與摘要儲存
│   ├── question_router.py       # 下一題推薦與語句生成
│   ├── utils/
│   │   └── vector_guard.py      # 向量庫檢查 fallback 工具
│
├── vector_builder/           # 向量處理模組
│   ├── embeddings.py            # 嵌入轉換工具（OpenAI Embedding）
│   ├── metadata_handler.py      # metadata 產業/主題分類
│   ├── pdf_processor.py         # PDF 解析與分段
│   ├── vector_store.py          # FAISS 儲存與載入
│
├── data/
│   ├── db_pdf_data/             # PDF 原始資料（不進 Git）
│   └── vector_output/           # 向量庫與 metadata 儲存
│       ├── faiss_index.index
│       ├── chunk_metadata.json
│       └── vector_build_record.json
```

---

## ⚙️ 安裝方式（本地）

```bash
git clone https://github.com/Jianjon/esg-gpt-bot.git
cd esg-gpt-bot
python -m venv venv
source venv/bin/activate  # 或 venv\Scripts\activate（Windows）
pip install -r requirements.txt
```

- 請將你的 OpenAI 金鑰存入 `.env`：
```bash
OPENAI_API_KEY=your-key-here
```

---

## 🧪 啟動方式

```bash
streamlit run src/consult_chat_app.py
```

> 或使用 `app.py` 統一入口啟動（未來整合更多頁面）

---

## 📚 向量資料庫建置流程

1. 將你的 PDF 文件放入 `data/db_pdf_data/` 的子資料夾中（如 `cases/`, `international/`, `taiwan/`）
2. 執行向量建置指令：

```bash
python build_vector_db.py
```

3. 系統會自動：
   - 分段 PDF
   - 提取段落 metadata（產業、主題、語言等）
   - 傳送到 OpenAI API 進行嵌入
   - 儲存為 `faiss_index.index` 和 `chunk_metadata.json`

4. 日後只會處理新增檔案（根據 `vector_build_record.json` 判斷）

---

## 🔐 Fallback 保護機制

- 所有使用到向量查詢的頁面（如顧問對談、報告生成）皆會自動檢查向量庫是否存在
- 若尚未建置，將提示使用者執行 `build_vector_db.py`，避免報錯

---

## 🧩 模組功能說明

| 模組名稱                  | 功能說明                           |
|---------------------------|------------------------------------|
| `consult_chat_app.py`     | 問答介面，顯示提問與記錄回答       |
| `context_tracker.py`      | 儲存上下文與摘要                   |
| `question_router.py`      | 控制提問順序與語言調整             |
| `vector_guard.py`         | fallback 檢查向量是否存在           |
| `pdf_processor.py`        | PDF 轉換段落（含分段規則）         |
| `metadata_handler.py`     | 分析 PDF 並標記主題/產業/語言等     |
| `vector_store.py`         | 儲存與載入向量資料庫（FAISS）      |

---

## 📌 TODO / 開發規劃

- [x] 顧問式問答模組
- [x] 向量資料庫建置流程
- [x] Fallback 錯誤處理機制
- [ ] 自由問答查詢頁
- [ ] 報告生成介面
- [ ] RAG 擴充與案例推薦

---

## 🧠 技術棧

- Python 3.10+
- Streamlit
- OpenAI GPT-4o / Embeddings
- LangChain（OpenAIEmbeddings, RecursiveCharacterTextSplitter）
- FAISS 向量儲存
- PyMuPDF (fitz), tqdm, dotenv

---

## 🙌 聯絡我

由 @Jianjon 製作，專為中小企業設計的 ESG 智能對話工具  
歡迎交流、協作、討論！

---
