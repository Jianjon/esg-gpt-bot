# src/utils/vector_guard.py

import streamlit as st
from pathlib import Path
from vector_builder.vector_store import VectorStore

def ensure_vector_ready():
    """
    如果向量庫尚未建置，顯示提示並停止執行
    用於 Streamlit 應用程式中的 fallback 機制
    """
    vector_store = VectorStore()
    vector_path = Path("data/vector_output")

    if not vector_store.exists(vector_path):
        st.warning("⚠️ 尚未建置知識庫，請先至後台執行向量建置流程（build_vector_db.py）。")
        st.stop()
