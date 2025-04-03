
# 📡 ESG GPT 顧問系統 API Reference

本文件整理目前系統提供的 Flask API 端點，涵蓋文件上傳、問題問答與報告產生等功能。

---

## 📁 API 總覽

| 方法 | 路徑              | 功能說明             |
|------|-------------------|----------------------|
| POST | `/upload`         | 上傳並處理 PDF 文件 |
| POST | `/ask`            | 提出問題並取得回答 |
| POST | `/generate_report`| 根據文件生成 ESG 報告 |

---

## 📨 `POST /upload`

### 📋 功能說明
上傳 PDF 文件，並建立對應的向量資料庫（存在記憶體中）。

### 🔧 請求格式
- Content-Type: `multipart/form-data`

#### ✅ 請求參數
| 參數名稱 | 類型     | 說明               |
|----------|----------|--------------------|
| `file`   | File     | 使用者上傳的 PDF 檔案 |

### 📤 範例 cURL
```bash
curl -X POST -F "file=@example.pdf" http://localhost:5000/upload
```

### 📨 成功回應
```json
{
  "message": "File uploaded and processed"
}
```

---

## 🧠 `POST /ask`

### 📋 功能說明
使用向量資料庫對問題進行查詢，並請 GPT 回答。

### 🔧 請求格式
- Content-Type: `application/json`

#### ✅ 請求參數
| 參數名稱   | 類型   | 說明               |
|------------|--------|--------------------|
| `question` | string | 使用者輸入的問題內容 |

### 📤 範例 cURL
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is carbon neutrality?"}'
```

### 📨 成功回應
```json
{
  "answer": "Carbon neutrality means..."
}
```

### ⚠️ 注意
- 使用前必須先執行 `/upload`，否則 `vectorstore` 尚未建立，會報錯

---

## 📄 `POST /generate_report`

### 📋 功能說明
請 GPT 產出一份 ESG 報告摘要，內容來自向量資料庫中讀到的 PDF 文件。

### 🔧 請求格式
無需傳參數，系統會自動組合 prompt

### 📤 範例 cURL
```bash
curl -X POST http://localhost:5000/generate_report
```

### 📨 成功回應
```json
{
  "report": "This company demonstrates ESG commitment by..."
}
```

---

## 🧱 系統記憶限制

| 條件                   | 行為                                   |
|------------------------|----------------------------------------|
| 沒有先執行 `/upload`   | `/ask` 或 `/generate_report` 將失敗    |
| 每次上傳新文件         | `vectorstore` 會被覆蓋，不保留歷史記憶 |

---

## ✅ 待改進（建議未來擴充）

| 功能項目              | 建議方向                         |
|------------------------|----------------------------------|
| 向量庫持久化           | 儲存於本地後再讀取               |
| 多用戶 session         | 支援多組 vectorstore 並隔離記憶 |
| 限制檔案大小與類型     | 僅允許 PDF，小於 10MB           |
| API token 認證機制     | 提高安全性                       |

---

若新增自由問答 API、報告格式選擇、自定義上傳類別等功能，請記得補上本文件。

```

---


