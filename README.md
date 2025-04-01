# esg-gpt-bot
An interactive ESG assistant powered by ChatGPT, designed for self-diagnosis, RAG feedback, and markdown reporting.
# ESG Assistant

An interactive assistant for ESG learning, diagnostics and reporting, powered by ChatGPT + local content.

## 🎯 Features
- Question-based user interaction
- GPT-enhanced feedback generation
- Lightweight CSV-based question pool
- Markdown-style summary report
- Modular Python architecture

## 📁 Folder Structure
- `/config`: environment or API settings
- `/modules`: functional modules like question handling and reporting
- `/data`: question sources or user input
- `/notes`: collaborative design notes

## 🚀 Getting Started
1. Duplicate `env_config_example.txt` as your local `.env`
2. Run `main.py` to launch the ESG assistant
3. Customize your logic inside `/modules`

## 💡 Vision
This project is designed for modular, explainable, and human-GPT collaborative ESG interaction.
# ESG 教學型問答系統（ESG-GPT-Bot）

本系統是一套針對 ESG 教學與診斷所設計的互動問答平台，結合 GPT 技術與結構化題庫，透過問答學習、自由提問、AI 回饋與報告產出，幫助企業深入理解溫室氣體盤查與永續治理概念。

---

## 系統架構模組

本系統由以下模組構成：

- `main.py`：主程式，負責流程控制與模組組裝
- `question_loader.py`：載入產業題庫
- `flow_controller.py`：流程與章節切換控制
- `answer_saver.py`：回答紀錄與版本管理
- `followup_engine.py`：延伸問題生成
- `response_engine.py`：自由問答與 GPT 回應
- `report_generator.py`：產出 500 / 1000 字報告
- `rag_engine.py`：整合本地知識庫 + GPT 回覆（RAG）
- `embedding_indexer.py`：將文件轉向量資料
- `ui_state_manager.py`：UI 呈現與互動控制
- `illustration_helper.py`：圖文說明輔助
- `topic_manager.py`：題庫載入與切換
- `version_comparator.py`（可選）：分析回答差異

---
## 題庫格式
請將題庫放置於 `data/` 目錄下，檔名格式：`questions_<industry>.csv`
CSV 欄位需包含：
- `id`, `section`, `text`, `options`, `explanation`, `followups`, `level`, `industry_tag`
---
## 向量知識庫（可選）
若需啟用 RAG 機制，請放入對應資料於 `knowledge_vector_db/`，並執行 `embedding_indexer.py` 產生索引。
---
## 設計理念
模組化、資料標準化、可維護、可擴充。未來支援多主題教學、診斷流程、自動摘要生成與跨模組串接。