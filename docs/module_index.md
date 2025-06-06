
# 🧩 模組索引：ESG GPT 顧問系統

本文件記錄專案所有核心模組、功能角色與彼此關聯，適用於開發維護、交接與擴充。

---

## 🗂️ 目錄架構總覽

```
esg-gpt-bot/
├── app.py
├── build_vector_db.py
├── requirements.txt
│
├── src/
│   ├── consult_chat_app.py
│   ├── welcome.py
│   ├── context_tracker.py
│   ├── question_router.py
│   └── utils/
│       └── vector_guard.py
│
├── vector_builder/
│   ├── pdf_processor.py
│   ├── embeddings.py
│   ├── metadata_handler.py
│   ├── vector_store.py
│
├── data/
│   ├── db_pdf_data/
│   └── vector_output/
```
---

## 📍 主介面模組（src/）

| 模組                            | 功能說明                                                                 |
|---------------------------------|--------------------------------------------------------------------------|
| `consult_chat_app.py`           | ESG 顧問對談介面，主要互動流程頁                                        |
| `welcome.py`                    | 使用者進入點，輸入姓名與產業資訊                                        |
| `context_tracker.py`           | 儲存每題使用者回答，並記錄 GPT 總結摘要                                |
| `question_router.py`           | 控制問卷流程，決定下一題邏輯，並將問題轉為自然語言                      |
| `utils/vector_guard.py`        | fallback 工具，確認向量庫存在，避免系統錯誤                            |

---

## 🧠 向量處理模組（vector_builder/）

| 模組                            | 功能說明                                                                 |
|---------------------------------|--------------------------------------------------------------------------|
| `pdf_processor.py`              | 將 PDF 每頁轉為文字，使用 LangChain 分段處理                            |
| `metadata_handler.py`           | 判斷每段落的主題、產業、地區與語言屬性                                 |
| `embeddings.py`                 | 呼叫 OpenAI Embedding API，將段落轉為向量                               |
| `vector_store.py`              | 控制向量儲存、讀取、快取檢查（FAISS）                                   |

---

## 🛠️ 向量建置腳本

| 檔案                         | 功能說明                                          |
|------------------------------|---------------------------------------------------|
| `build_vector_db.py`         | 建置向量庫主腳本，支援快取與略過已處理 PDF       |
| `vector_output/`             | 儲存向量資料庫（faiss_index.index + metadata）   |
| `vector_build_record.json`   | 記錄已處理過的 PDF 路徑，避免重複處理             |

---

## 📁 資料結構說明（data/）

| 資料夾                         | 說明                                             |
|--------------------------------|--------------------------------------------------|
| `data/db_pdf_data/`            | 原始 PDF 知識資料（分國際、台灣、案例）         |
| `data/vector_output/`          | 儲存向量資料庫與處理紀錄                        |

---

## 🧩 模組互動流程（簡圖）

```mermaid
flowchart TD
    A[PDF 檔案] --> B[PDFProcessor 分段]
    B --> C[MetadataHandler 標記主題/產業]
    C --> D[Embeddings 嵌入向量]
    D --> E[VectorStore 儲存向量+metadata]
    E --> F[向量儲存至 FAISS]

    subgraph Streamlit 問卷流程
        G[使用者回答問題]
        G --> H[ContextTracker 紀錄回答 + 總結]
        H --> I[VectorStore 查詢相關知識]
    end
```

---

## 🔄 模組可擴充性建議

| 功能場景             | 建議模組擴充名稱              | 備註                           |
|----------------------|-------------------------------|--------------------------------|
| 報告生成             | `report_generator_app.py`      | 可依回答自動撰寫摘要建議       |
| 自由問答查詢         | `free_qa.py`                   | 可呼叫向量庫進行知識查詢       |
| RAG 文本補充         | `retriever_engine.py`          | 結合 metadata 做來源引用        |
| 上傳新文件           | `pdf_upload_app.py`            | 供管理者加入新知識             |

---
### 🤖 Guided RAG 問答模組（引導式自由問答）

模組：`src/managers/guided_rag.py`

此模組負責在問卷過程中提供一種「引導式自由問答」的體驗，讓使用者能針對每一題主動提問，並透過最多三輪互動協助選出合適選項。

- 啟用時機：
  - 所有問卷題目皆支援
  - 使用者輸入自由提問或點選「不知道」

- 流程設計：
  1. 使用者輸入疑問或點選「不知道」
  2. 系統查詢向量資料庫取得相關內容
  3. 呼叫 GPT-4o 回答（並顯示引用段落）
  4. 最多三輪互動後：
     - 若選出選項 → 儲存
     - 若仍無法回答 → 顯示「跳過此題也沒關係」提示並記錄未答

- 對話紀錄追蹤：
  - 使用 `st.session_state['guided_chat']` 儲存互動紀錄
  - 使用 `guided_turns` 控制輪次與結束條件

- 顯示樣式：
  - 系統回覆顯示為顧問氣泡（ai-message）
  - 引用來源以摺疊段落顯示（含檔名與頁碼）

- 關聯模組：
  - `consult_chat_app.py`：主介面整合點
  - `vector_store.py`：提供向量查詢
  - `prompt_template.md`：未來可分離成引導語氣模板

此模組提升問卷的教育性與理解性，是 ESG 顧問系統的核心亮點之一。

## ✅ 最後備註

- 本專案已具備完整資料流與模組邊界
- 未來模組開發請維持相同風格：**職責單一、命名清晰、可維護**
- 若有新成員加入，建議先閱讀本檔案與 `README.md`

```
