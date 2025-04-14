# 📂 src/utils/rag_retriever.py

from pathlib import Path
from typing import List, Dict
from vector_builder.vector_store import VectorStore

class RAGRetriever:
    """
    RAG 向量段落擷取模組
    - 載入指定子資料夾的向量庫
    - 查詢相關段落（for GPT 回答 / 報告輔助）
    """
    def __init__(self, vector_root: str = "data/vector_output_hf"):
        self.vector_root = Path(vector_root)
        self.loaded_stores: Dict[str, VectorStore] = {}

    def _load_store(self, folder_name: str) -> VectorStore:
        if folder_name in self.loaded_stores:
            return self.loaded_stores[folder_name]

        vector_path = self.vector_root / folder_name
        if not vector_path.exists():
            raise FileNotFoundError(f"❌ 找不到向量資料夾：{vector_path}")

        store = VectorStore()
        store.load(vector_path)
        self.loaded_stores[folder_name] = store
        return store

    def search_chunks(self, query: str, doc_folder: str, top_k: int = 5) -> List[Dict]:
        store = self._load_store(doc_folder)
        return store.search(query, top_k=top_k)

    def get_context(self, query: str, doc_folder: str, top_k: int = 5) -> str:
        chunks = self.search_chunks(query, doc_folder, top_k=top_k)
        return "\n\n".join([c.get("text", "") for c in chunks])


# ✅ 提供外部使用的簡化接口
_rag_retriever = RAGRetriever()

def get_rag_context_for_question(question_text: str, rag_doc: str = None, top_k: int = 3) -> str:
    """
    提供外部模組使用的簡化接口：
    - 輸入題目文字與指定資料夾名稱（如：ISO_14064-1）
    - 回傳向量擷取的段落文字（預設 3 段）
    """
    if not rag_doc:
        return ""
    try:
        return _rag_retriever.get_context(query=question_text, doc_folder=rag_doc, top_k=top_k)
    except Exception as e:
        return f"⚠️ 無法取得 RAG 段落：{str(e)}"
