# 🧠 ESG 顧問互動系統流程規劃（System Flow Plan）

本文件描述 ESG GPT 顧問系統的整體邏輯流程、作答階段、系統記憶與資料建置方式。

---

## 一、使用者互動流程概述

1. 使用者輸入姓名與選擇產業
2. 進入教學導向測試題（5 題）
3. 進入初階問題（25 題）
4. 完成初階後可選擇進階題（30-35 題）
5. 每題為單選/複選選項 + 顧問引導式問法
6. 最後可生成摘要報告（初階：500 字 / 進階：1000 字）
7. 所有對話與作答皆可記錄並回顧

---

## 二、問卷設計原則

- 題目依產業客製化
- 題庫儲存在 `/data/*.csv` 中
- 題目類型為 single / multiple，不考慮正確答案
- 題庫欄位固定：`id, stage, topic, text, options, type, hint`
- 初階與進階題目分開，不可自由跳題
- 題號設計：教學導向為 `S000–S004`，其餘為產業別編號

---

## 三、作答流程控制（AnswerSession）

- 每位使用者進入問卷後建立 `AnswerSession`
- 可逐題記錄回答
- 使用 `get_current_question()` 控制流程
- 若全部作答完畢，自動顯示完成畫面與摘要

---

## 四、顧問模式（consult_chat_app.py）

- 每一題轉為顧問式語句，由 GPT-4o 生成自然提問
- 使用者輸入回應後：
  - 記錄作答
  - 呼叫 `context_tracker.py` 儲存該題摘要
- 顯示歷史對話：`st.chat_message(...)`
- 所有內容儲存在 `st.session_state.chat_history`、`consult_session` 中

---

## 五、報告生成與向量查詢（未來擴充）

- 報告生成將整合所有作答與摘要
- 支援呼叫向量庫（RAG）補充建議文字
- 產業別可對應 baseline 建議值
- 若有完整回應紀錄，也可結合圖表呈現

---

## 六、使用者狀態與記憶機制

- 所有狀態皆使用 `st.session_state` 管理：

| 欄位名稱             | 說明                                   |
|----------------------|----------------------------------------|
| `user_name`          | 使用者名稱                             |
| `industry`           | 所選產業（如 restaurant, logistics）    |
| `stage`              | 問卷階段（basic / advanced）           |
| `consult_session`    | 問卷作答控制模組                       |
| `chat_history`       | 顧問模式下的對話紀錄                   |
| `vector_store`       | FAISS 向量庫載入物件（由 fallback 管理）|

- 設計原則：
  - 缺少任一狀態會停止流程
  - 可延伸加入 `start_time`、`finish_time` 供統計使用

---

## 七、向量查詢流程圖（RAG）

```mermaid
flowchart TD
    A[使用者輸入問題] --> B[查找向量資料庫（FAISS）]
    B --> C[找出最相近段落（Top-k）]
    C --> D[組合成 Prompt 提供背景知識]
    D --> E[傳送至 GPT-4o 模型]
    E --> F[輸出自然語言回答]

