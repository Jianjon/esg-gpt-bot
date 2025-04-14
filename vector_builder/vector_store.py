# vector_builder/vector_store.py
import json
from pathlib import Path
import logging
from typing import List, Dict
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embed_model = SentenceTransformer(self.model_name)
        self.dimension = self.embed_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata: List[Dict] = []

    def reset(self):
        """
        重設索引與 metadata，用於重新建構整個向量資料庫。
        """
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    def get_query_vector(self, text: str) -> List[float]:
        return self.embed_model.encode(text, convert_to_numpy=True).tolist()

    def add_vectors(self, vectors: List[List[float]], metadata_list: List[Dict]):
        self.index.add(np.array(vectors).astype("float32"))
        self.metadata.extend(metadata_list)

    def save(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(output_dir / 'faiss_index.index'))

        with open(output_dir / 'chunk_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        vector_info = {
            "vector_dim": self.dimension,
            "model": self.model_name
        }
        with open(output_dir / 'vector_info.json', 'w', encoding='utf-8') as f:
            json.dump(vector_info, f, ensure_ascii=False, indent=2)

        logging.info("向量資料與 metadata 已儲存至 %s", output_dir)

    def load(self, output_dir):
        output_dir = Path(output_dir)
        index_path = output_dir / 'faiss_index.index'
        metadata_path = output_dir / 'chunk_metadata.json'
        info_path = output_dir / 'vector_info.json'

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError("找不到 faiss_index.index 或 chunk_metadata.json")

        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        if info_path.exists():
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                if info["vector_dim"] != self.dimension:
                    raise ValueError(f"向量維度不一致：index 為 {info['vector_dim']}，目前為 {self.dimension}")
                if info["model"] != self.model_name:
                    logging.warning("⚠️ 模型名稱不一致：index 為 %s，目前為 %s", info["model"], self.model_name)
        else:
            logging.warning("⚠️ 未偵測到 vector_info.json，請確認相容性")

    def exists(self, output_dir) -> bool:
        output_dir = Path(output_dir)
        return all([
            (output_dir / 'faiss_index.index').exists(),
            (output_dir / 'chunk_metadata.json').exists(),
            (output_dir / 'vector_info.json').exists()
        ])

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.metadata:
            return []

        query_vec = self.get_query_vector(query)
        query_vec = np.array([query_vec], dtype="float32")

        if query_vec.shape[1] != self.index.d:
            raise ValueError(f"查詢向量維度 {query_vec.shape[1]} 與索引維度 {self.index.d} 不一致")

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                chunk = self.metadata[idx].copy()
                chunk["score"] = float(score)
                results.append(chunk)
        return results