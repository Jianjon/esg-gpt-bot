# check_vector_index_info.py

import faiss
import json
from pathlib import Path

VECTOR_DIR = Path("data/vector_output/")

index_path = VECTOR_DIR / "faiss_index.index"
meta_path = VECTOR_DIR / "chunk_metadata.json"
info_path = VECTOR_DIR / "vector_info.json"

print("🚀 正在檢查向量資料庫狀態...\n")

# 1️⃣ 檢查 FAISS index 維度
if index_path.exists():
    index = faiss.read_index(str(index_path))
    print(f"✅ FAISS index 存在，維度為：{index.d}")
else:
    print("❌ 找不到 faiss_index.index")

# 2️⃣ 檢查 metadata 數量
if meta_path.exists():
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"✅ metadata 筆數為：{len(metadata)}")
else:
    print("❌ 找不到 chunk_metadata.json")

# 3️⃣ 檢查 vector_info.json 的設定
if info_path.exists():
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    print(f"✅ vector_info.json 記錄：維度 = {info.get('vector_dim')}, 模型 = {info.get('model')}")
    if info.get("vector_dim") != 1536:
        print("⚠️ 警告：目前設定非 OpenAI 的向量維度（應為 1536）")
    if "openai" not in info.get("model", "").lower() and "ada" not in info.get("model", "").lower():
        print("⚠️ 警告：目前模型可能不是 OpenAIEmbeddings 建立的")
else:
    print("❌ 找不到 vector_info.json")
