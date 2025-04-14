# test_vector_search.py
from vector_builder.vector_store import VectorStore

vector_path = "data/vector_output_hf"
store = VectorStore(model_name="sentence-transformers/all-MiniLM-L6-v2")
store.load(vector_path)

query = "什麼是範疇三排放？"
print(f"\n🔍 測試查詢：{query}\n")

results = store.search(query, top_k=5)

if not results:
    print("⚠️ 沒有找到相關段落。")
else:
    for i, r in enumerate(results, 1):
        print(f"[{i}] 相似度分數：{r['score']:.4f}")
        print(r['text'][:200].strip().replace('\n', ' ') + "...")
        print("---")
