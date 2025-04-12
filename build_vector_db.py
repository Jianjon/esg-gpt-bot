"""
向量資料庫建置腳本
處理 PDF 並建立 FAISS 向量與 metadata，並記錄已處理檔案
"""

from pathlib import Path
import json
import logging
from tqdm import tqdm
from vector_builder import PDFProcessor, MetadataHandler
from vector_builder.embeddings import get_embedding
from vector_builder.vector_store import VectorStore

def load_processed_record(record_path: Path) -> dict:
    if record_path.exists():
        with open(record_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_processed_record(record_path: Path, record: dict):
    with open(record_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

def main():
    # 初始化
    pdf_processor = PDFProcessor()
    metadata_handler = MetadataHandler()
    vector_store = VectorStore()

    base_dir = Path("data/db_pdf_data")
    output_dir = "data/vector_output"  # ✅ 傳 str，VectorStore 內部會自動轉 Path

    log_file = Path(output_dir) / "build_log.txt"
    record_file = Path(output_dir) / "vector_build_record.json"
    processed_record = load_processed_record(record_file)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    print("開始向量資料庫建置...")
    logging.info("=== 啟動建置程序 ===")

    all_vectors = []
    all_metadata = []

    folder_list = ["cases", "international", "taiwan"]
    pdf_paths = [p for folder in folder_list for p in (base_dir / folder).rglob("*.pdf")]

    for pdf_path in tqdm(pdf_paths, desc="📁 總體進度"):
        file_id = str(pdf_path.resolve())
        if file_id in processed_record:
            print(f"🟡 略過已處理：{pdf_path.name}")
            continue

        print(f"\n📄 處理檔案：{pdf_path.name}")
        logging.info(f"處理：{pdf_path.name}")

        chunks = pdf_processor.process_pdf(pdf_path)
        for chunk_text, raw_meta in tqdm(chunks, desc="🔹 分段與嵌入", leave=False):
            enriched = metadata_handler.enrich_metadata(raw_meta, chunk_text)
            enriched["text"] = chunk_text  # ✅ 關鍵：讓 chunk 有 'text' 欄位
            
            try:
                vector = get_embedding(chunk_text)
                all_vectors.append(vector)
                all_metadata.append(enriched)
            except Exception as e:
                logging.error(f"向量嵌入失敗：{e}")

        processed_record[file_id] = {"filename": pdf_path.name}
        save_processed_record(record_file, processed_record)

    if all_vectors:
        vector_store.add_vectors(all_vectors, all_metadata)
        vector_store.save(output_dir)
        print("✅ 向量儲存完成")
        logging.info(f"完成：共處理 {len(all_vectors)} 筆向量")
    else:
        print("⚠️ 沒有新的向量需要儲存")

if __name__ == "__main__":
    main()
