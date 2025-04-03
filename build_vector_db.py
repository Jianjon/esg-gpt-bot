"""
向量資料庫建置腳本
用於處理 PDF 文件並建立向量資料庫
"""

from pathlib import Path
import json
import numpy as np
import faiss
from vector_builder import PDFProcessor, MetadataHandler
from vector_builder.embeddings import get_embedding
import logging
from tqdm import tqdm
import time

def main():
    # 初始化模組
    pdf_processor = PDFProcessor()
    metadata_handler = MetadataHandler()

    # 設定資料夾路徑
    base_dir = Path("data/db_pdf_data")
    output_dir = Path("data/vector_output")
    output_dir.mkdir(exist_ok=True, parents=True)

    # 初始儲存容器
    vector_list = []
    metadata_list = []

    # 啟用日誌
    logging.basicConfig(
        filename=output_dir / "build_log.txt",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info("開始向量庫建置")
    print("開始向量庫建置...")

    # 計算總 PDF 數量
    total_pdfs = 0
    for folder_name in ["cases", "international", "taiwan"]:
        folder_path = base_dir / folder_name
        total_pdfs += len(list(folder_path.rglob("*.pdf")))
    
    print(f"總共發現 {total_pdfs} 個 PDF 檔案")
    processed_pdfs = 0
    total_chunks = 0

    # 處理每個 PDF 檔案
    for folder_name in ["cases", "international", "taiwan"]:
        folder_path = base_dir / folder_name
        pdf_files = list(folder_path.rglob("*.pdf"))
        
        print(f"\n處理資料夾：{folder_name}，共 {len(pdf_files)} 份 PDF")
        logging.info(f"處理資料夾：{folder_name}，共 {len(pdf_files)} 份 PDF")

        # 使用 tqdm 顯示每個資料夾的進度
        for pdf_path in tqdm(pdf_files, desc=f"處理 {folder_name} 資料夾"):
            logging.info(f"處理 PDF：{pdf_path.name}")
            chunks = pdf_processor.process_pdf(pdf_path)
            
            # 顯示當前 PDF 的處理進度
            print(f"\n處理檔案：{pdf_path.name}")
            print(f"分段數量：{len(chunks)}")
            
            # 使用 tqdm 顯示 chunks 處理進度
            for chunk_text, raw_metadata in tqdm(chunks, desc="生成向量", leave=False):
                enriched = metadata_handler.enrich_metadata(raw_metadata, chunk_text)
                
                try:
                    vector = get_embedding(chunk_text)
                    vector_list.append(vector)
                    metadata_list.append(enriched)
                    total_chunks += 1
                except Exception as e:
                    logging.error(f"嵌入失敗：{e}")
            
            processed_pdfs += 1
            print(f"進度：{processed_pdfs}/{total_pdfs} PDFs ({processed_pdfs/total_pdfs*100:.1f}%)")
            print(f"已處理段落：{total_chunks} 段")

    # 儲存 FAISS index
    print("\n儲存向量索引...")
    dimension = 1536
    index = faiss.IndexFlatIP(dimension)
    index.add(np.array(vector_list).astype("float32"))
    faiss.write_index(index, str(output_dir / "faiss_index.index"))
    logging.info(f"已儲存 FAISS index，共 {len(vector_list)} 筆向量")

    # 儲存 metadata
    print("儲存 metadata...")
    with open(output_dir / "chunk_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    logging.info(f"已儲存 metadata，共 {len(metadata_list)} 筆段落")

    print(f"\n✅ 向量庫建置完成！")
    print(f"處理統計：")
    print(f"- 總 PDF 數：{total_pdfs}")
    print(f"- 總段落數：{total_chunks}")
    print(f"資料輸出至：{output_dir}")

if __name__ == "__main__":
    main() 