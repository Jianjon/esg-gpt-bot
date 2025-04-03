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
