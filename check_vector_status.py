# check_vector_status.py
# ✅ 用絕對路徑比對已建檔案，並顯示相對路徑避免報錯

import os
import json
from pathlib import Path

# === 參數設定 ===
PDF_ROOT = Path("data/db_pdf_data").resolve()
VECTOR_ROOT = Path("data/vector_output_hf")
VECTOR_METADATA = VECTOR_ROOT / "vector_build_record.json"

# === 讀取已建置紀錄（絕對路徑為 key） ===
if VECTOR_METADATA.exists():
    with open(VECTOR_METADATA, "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    metadata = {}

# === 掃描所有 PDF 並比對 ===
missing_vectors = []
existing_vectors = []

for folder_path, _, files in os.walk(PDF_ROOT):
    for fname in files:
        if fname.lower().endswith(".pdf"):
            full_path = Path(os.path.join(folder_path, fname)).resolve()
            full_path_str = str(full_path)

            if full_path_str in metadata:
                existing_vectors.append(full_path)
            else:
                missing_vectors.append(full_path)

# === 顯示結果 ===
print("\n📁 掃描完成：PDF 資料庫向量化狀態")
print("=" * 50)
print(f"✅ 已建置向量庫：{len(existing_vectors)} 筆")
for path in existing_vectors:
    print(f"    - {path.relative_to(PDF_ROOT)}")

print(f"\n❌ 尚未建置向量庫：{len(missing_vectors)} 筆")
for path in missing_vectors:
    print(f"    - {path.relative_to(PDF_ROOT)}")

print("\n✅ 本程式不會呼叫 OpenAI API，不會產生任何費用")