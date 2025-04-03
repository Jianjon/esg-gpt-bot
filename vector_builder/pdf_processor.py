"""
PDF 處理模組
負責讀取 PDF 文件並進行分段處理
"""

from pathlib import Path
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", ".", "!", "?", "！", "？"],
            keep_separator=True
        )
        
    def process_pdf(self, pdf_path: Path) -> List[Tuple[str, Dict]]:
        """處理單個PDF文件，返回chunks和對應的metadata"""
        try:
            doc = fitz.open(str(pdf_path))
            chunks_with_metadata = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                    
                # 分段
                chunks = self.text_splitter.split_text(text)
                
                # 為每個chunk創建metadata
                for chunk_num, chunk in enumerate(chunks):
                    chunk_lines = chunk.split('\n')
                    title = chunk_lines[0].strip() if chunk_lines else ""
                    
                    metadata = {
                        "chunk_id": f"{pdf_path.stem}-p{page_num+1}-s{chunk_num+1}",
                        "source": pdf_path.name,
                        "path": str(pdf_path.parent.relative_to(pdf_path.parent.parent)),
                        "page": page_num + 1,
                        "title": title,
                        "text": chunk  # 保存原始文本，用於後續處理
                    }
                    
                    chunks_with_metadata.append((chunk, metadata))
            
            doc.close()
            return chunks_with_metadata
            
        except Exception as e:
            logging.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
            
    def get_token_count(self, text: str) -> int:
        """估算token數量（簡單實現，實際應使用tiktoken）"""
        return len(text.split()) 