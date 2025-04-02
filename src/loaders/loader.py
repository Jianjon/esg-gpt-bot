from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

DOCS_PATH = "data/docs"

# 載入單一檔案

def load_file(filepath):
    if filepath.endswith(".pdf"):
        loader = PyPDFLoader(filepath)
    elif filepath.endswith(".txt"):
        loader = TextLoader(filepath, encoding="utf-8")
    else:
        raise ValueError("不支援的檔案類型: " + filepath)
    return loader.load()

# 載入整個資料夾

def load_all_documents():
    docs = []
    for fname in os.listdir(DOCS_PATH):
        fpath = os.path.join(DOCS_PATH, fname)
        try:
            docs.extend(load_file(fpath))
        except Exception as e:
            print(f"⚠️ 跳過 {fname}: {e}")
    return docs

# 分段器：控制向量切片大小

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)
