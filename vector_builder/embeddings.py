# vector_builder/embeddings.py
from sentence_transformers import SentenceTransformer

# 初始化模型（可根據實際使用換模型名）
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    """
    使用 HuggingFace 模型將文本轉為向量
    Args:
        text (str): 要轉換的文字
    Returns:
        List[float]: 向量表示
    """
    return model.encode(text, convert_to_numpy=True).tolist()

if __name__ == "__main__":
    print("🔍 測試 get_embedding()：")
    vec = get_embedding("永續發展與淨零碳排的關係")
    print(f"✅ 向量長度：{len(vec)}")
    print(vec[:5], "...")
