
# 🧠 向量資料結構與查詢設計（Vector Structure & RAG Metadata）

本文件說明 ESG GPT 顧問系統中向量資料的設計、儲存方式與 metadata 欄位定義，協助開發者進行建置、查詢與擴充。

---

## 一、資料來源與建置流程

向量資料由 `data/db_pdf_data/` 中的 PDF 轉換而來，使用下列流程處理：

1. 透過 `PDFProcessor` 將 PDF 分頁、擷取文字與段落切分
2. 每段文字透過 `OpenAIEmbeddings` 轉為 1536 維向量
3. 同時產生 metadata（段落描述資訊）
4. 向量與 metadata 一起儲存在 FAISS 向量庫

---

## 二、儲存檔案位置

```bash
data/vector_output/
├── faiss_index.index          # 儲存向量的主體（由 FAISS 管理）
├── chunk_metadata.json        # 儲存每個向量對應的 metadata
├── vector_build_record.json   # 已建置檔案的快取記錄（避免重複處理）
├── build_log.txt              # 處理紀錄與錯誤訊息
```

---

## 三、每筆段落資料包含哪些欄位？

每個向量段落的 metadata 格式如下：

```json
{
  "chunk_id": "ISO20400-p3-s2",
  "source": "ISO_20400_2017E.pdf",
  "path": "international/sustainable_procurement",
  "page": 3,
  "title": "3 Principles of sustainable procurement",
  "main_topic": "sustainability",
  "industry": "cross_industry",
  "region": "global",
  "language": "en"
}
```

---

## 四、欄位定義說明

| 欄位名稱     | 類型    | 說明與來源                                                       |
|--------------|---------|------------------------------------------------------------------|
| `chunk_id`   | string  | 每段唯一 ID，格式為 `檔名-p頁碼-s段落序號`                      |
| `source`     | string  | 原始 PDF 檔名                                                    |
| `path`       | string  | 相對資料夾路徑，標示資料分區（如 `cases`, `international/...`） |
| `page`       | int     | 此段原始出現在 PDF 第幾頁                                        |
| `title`      | string  | 段落首行文字（預設作為標題）                                     |
| `main_topic` | string  | 主題分類（如 sustainability, climate, governance, social）       |
| `industry`   | string  | 對應產業分類（retail, logistics...）                              |
| `region`     | string  | 區域：`taiwan`、`global`、`unknown`                               |
| `language`   | string  | 語言標記：`en` 或 `zh`（依中文字比例判斷）                         |

---

## 五、建置流程來源模組

| 模組名稱              | 功能說明                       |
|-----------------------|--------------------------------|
| `pdf_processor.py`     | 分頁、擷取文字與段落切分       |
| `metadata_handler.py`  | 提取主題、產業、地區、語言等標記 |
| `embeddings.py`        | 呼叫 OpenAI API 做向量轉換     |
| `vector_store.py`      | 儲存向量與 metadata             |

---

## 六、查詢方式與擴充建議（RAG 應用）

查詢向量庫時，可用的檢索條件包含：

- ✏️ `metadata["main_topic"]`：只查永續、治理或氣候主題段落
- 🌍 `metadata["region"]`：限定台灣或國際來源
- 🏢 `metadata["industry"]`：只取零售業或物流業段落
- 🈁 `metadata["language"]`：可針對中文段落建立提示

---

## 七、建議擴充欄位（選用）

| 欄位名稱         | 用途                             |
|------------------|----------------------------------|
| `source_url`     | 來源網址（若非本地 PDF）         |
| `created_at`     | 建置時間戳                        |
| `content_hash`   | 原始段落摘要雜湊，供版本追蹤使用 |
| `token_count`    | 預估 token 數量（控制提示成本）   |

---

## 八、FAISS 查詢範例（內部用途）

```python
results = vector_store.index.search(
    query_vector,
    k=3
)

# 回傳向量相似度前 3 名段落
# 可用 results.metadata[i] 檢查主題與產業
```

---

## ✅ 最佳實務總結

- 📁 將向量庫儲存與原始 PDF 完全分離
- ✅ metadata 可靈活擴充與查詢過濾
- 🚫 避免一次查太多向量，建議 k=3~5
- ✨ 可搭配提示語 `You are given the following reference...` 提升回答可信度

```

---
