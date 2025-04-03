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
from vector_builder.vector_store import VectorStore
import logging
from tqdm import tqdm
import time

def main():
    # 初始化模組
    pdf_processor = PDFProcessor()
    metadata_handler = MetadataHandler()
    vector_store = VectorStore()

    # 設定資料夾路徑
    base_dir = Path("data/db_pdf_data")
    output_dir = Path("data/vector_output")
    output_dir.mkdir(exist_ok=True, parents=True)

    # 啟用日誌
    logging.basicConfig(
        filename=output_dir / "build_log.txt",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("=== 開始向量庫建置 ===")
    print("開始向量庫建置...")

    # 快取檢查：若向量資料庫已存在，則跳過建置
    if vector_store.exists(output_dir):
        print("✅ 已偵測到已建置的向量庫，跳過建置流程。")
        logging.info("偵測到向量庫已存在，跳過建置。")
        return

    # 初始化儲存容器
    vector_list = []
    metadata_list = []

    # 計算總 PDF 數量
    total_pdfs = sum(len(list((base_dir / folder).rglob("*.pdf")))
                     for folder in ["cases", "international", "taiwan"])
    print(f"總共發現 {total_pdfs} 個 PDF 檔案")

    processed_pdfs = 0
    total_chunks = 0

    for folder_name in ["cases", "international", "taiwan"]:
        folder_path = base_dir / folder_name
        pdf_files = list(folder_path.rglob("*.pdf"))

        print(f"\n處理資料夾：{folder_name}，共 {len(pdf_files)} 份 PDF")
        logging.info(f"處理資料夾：{folder_name}，共 {len(pdf_files)} 份 PDF")

        for pdf_path in tqdm(pdf_files, desc=f"處理 {folder_name} 資料夾"):
            logging.info(f"處理 PDF：{pdf_path.name}")
            chunks = pdf_processor.process_pdf(pdf_path)

            print(f"\n處理檔案：{pdf_path.name}")
            print(f"分段數量：{len(chunks)}")

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

    # 儲存 FAISS 向量與 metadata
    print("\n儲存向量索引...")
    vector_store.add_vectors(vector_list, metadata_list)
    vector_store.save(output_dir)
    print("✅ 向量資料庫已儲存")
    logging.info("=== 向量建置完成，共儲存 %d 筆段落 ===", total_chunks)


if __name__ == "__main__":
    main()
