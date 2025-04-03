"""
向量嵌入模組
負責將文本轉換為向量表示
"""

from typing import List
import numpy as np
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def get_embedding(text: str) -> List[float]:
    """
    使用 OpenAI 的 API 將文本轉換為向量表示
    
    Args:
        text: 要轉換的文本
        
    Returns:
        向量表示
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1536
    )
    return embeddings.embed_query(text)

def get_embedding_old(text: str) -> List[float]:
    """
    將文本轉換為向量表示
    
    Args:
        text: 輸入文本
        
    Returns:
        1536 維的向量表示
    """
    try:
        # 使用 OpenAI 的嵌入模型
        vector = get_embedding(text)
        return vector
    except Exception as e:
        raise Exception(f"向量嵌入失敗：{str(e)}") 