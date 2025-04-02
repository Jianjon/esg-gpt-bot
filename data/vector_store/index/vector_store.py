from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import os

VECTOR_STORE_PATH = "data/vector_store/index"

def build_vector_store(documents):
    embeddings = OpenAIEmbeddings()
    store = FAISS.from_documents(documents, embedding=embeddings)
    os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
    store.save_local(VECTOR_STORE_PATH)
    return store

def load_vector_store():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(VECTOR_STORE_PATH, embeddings)
