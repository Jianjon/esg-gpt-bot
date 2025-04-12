"""
向量嵌入模組
負責將文本轉換為向量表示
"""

from typing import List
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


import os

# 載入 .env 設定
load_dotenv()

# ✅ 僅初始化一次（可全域共用）
embedding_model = OpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    dimensions=int(os.getenv("EMBEDDING_DIM", "1536"))
)

def get_embedding(text: str) -> List[float]:
    """
    使用 OpenAI 將文本轉為向量
    Args:
        text (str): 要轉換的文字
    Returns:
        List[float]: 向量表示
    """
    try:
        return embedding_model.embed_query(text)
    except Exception as e:
        raise RuntimeError(f"❌ 向量嵌入失敗：{e}")

# ✅ 選擇保留或刪除這個
def get_embedding_old(text: str) -> List[float]:
    return get_embedding(text)

# ✅ 可選：測試用主程式段
if __name__ == "__main__":
    print("🔍 測試 get_embedding()：")
    vec = get_embedding("永續發展與淨零碳排的關係")
    print(f"✅ 向量長度：{len(vec)}")
    print(vec[:5], "...")  # 顯示前五個維度
