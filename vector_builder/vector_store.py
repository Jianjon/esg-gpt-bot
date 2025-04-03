# vector_builder/vector_store.py

from pathlib import Path
import faiss
import json
import os
from typing import List, Dict
import logging

class VectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata: List[Dict] = []

    def add_vectors(self, vectors: List[List[float]], metadata_list: List[Dict]):
        self.index.add(vectors)
        self.metadata.extend(metadata_list)

    def save(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(output_dir / 'faiss_index.index'))
        with open(output_dir / 'chunk_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        logging.info("Vector index and metadata saved to %s", output_dir)

    def load(self, output_dir: Path):
        index_path = output_dir / 'faiss_index.index'
        metadata_path = output_dir / 'chunk_metadata.json'

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError("Vector index or metadata not found")

        self.index = faiss.read_index(str(index_path))
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        logging.info("Vector index and metadata loaded from %s", output_dir)

    def exists(self, output_dir: Path) -> bool:
        return (output_dir / 'faiss_index.index').exists() and (output_dir / 'chunk_metadata.json').exists()
