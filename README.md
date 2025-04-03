
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
# Guided RAG 使用說明

本模組整合於 `consult_chat_app.py`，透過向量庫 + GPT-4o 實現引導式自由問答，協助使用者在不清楚如何回答問卷時提供漸進式提示。

---

## 🎯 功能定位

| 功能            | 說明 |
|------------------|------|
| 啟動條件         | 問卷中任一題皆可進入引導問答區 |
| 啟動方式         | 使用者輸入問題或「不知道」 |
| 查詢方式         | 使用內建 FAISS 向量庫進行語意搜尋 |
| 回答模型         | OpenAI GPT-4o（可改為 3.5） |
| 最多互動次數     | 3 輪引導對話 |
| 結束條件         | 使用者輸入答案或選擇「跳過此題」 |


## 🧩 模組結構

### 1. `src/managers/guided_rag.py`

| 方法             | 說明 |
|------------------|------|
| `__init__()`      | 載入向量庫與模型設定 |
| `search_related_chunks()` | 查詢與輸入問題最相關的段落 |
| `build_prompt()` | 建構 RAG 回答提示語（含 context）|
| `ask()`           | 執行查詢與回應邏輯，回傳 GPT 回答與引用內容 |


### 2. 修改 `consult_chat_app.py`

- 建立 `guided_rag` 實例並檢查向量庫存在
- 使用 `st.session_state['guided_turns']` 控制回合數
- 使用 `st.session_state['guided_chat']` 紀錄上下文對話
- 每題最多 3 輪互動後提供「跳過」按鈕
- 若點選跳過，自動標記作答為「未回答」並進入下一題


## 🧠 Prompt 設計（範例）

```text
你是一位專業的永續顧問，正在引導客戶完成 ESG 問卷。
根據以下背景資料，請幫助使用者理解問題，並試著引導對方選出適當的選項。
若使用者說「不知道」或無法回答，請進一步說明或提供範例幫助其理解。
```


## 📝 其他設計說明

- 每輪 GPT 回應後提供 2–3 個方向性建議，協助使用者思考
- 顧問回應與使用者問題均記錄於 `guided_chat` session 中
- 顯示 chunk 來源檔名與頁碼，協助引用與驗證
- 使用者回覆任意文字皆視為作答完成（非一定要選項）
- 設計考量以教育與診斷為導向，非考試

---

此模組可與報告生成整合，作為額外的參考資料來源。
未來也可延伸做「使用者困難統計」、「未回答題標記」、「常見問題收斂」等應用。

---

## 🙌 聯絡我

由 @Jianjon 製作，專為中小企業設計的 ESG 智能對話工具  
歡迎交流、協作、討論！

---
