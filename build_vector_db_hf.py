# build_vector_db_hf.py
"""
使用 HuggingFace 模型建立向量資料庫（不會產生 OpenAI 費用）
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
    pdf_processor = PDFProcessor()
    metadata_handler = MetadataHandler()
    vector_store = VectorStore()

    base_dir = Path("data/db_pdf_data")
    output_dir = Path("data/vector_output_hf")

    log_file = output_dir / "build_log.txt"
    record_file = output_dir / "vector_build_record.json"
    processed_record = load_processed_record(record_file)

    output_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    print("開始向量資料庫建置...")
    logging.info("=== 啟動建置程序 ===")

    folder_list = ["cases", "international", "taiwan"]
    pdf_paths = [p for folder in folder_list for p in (base_dir / folder).rglob("*.pdf")]

    for pdf_path in tqdm(pdf_paths, desc="📁 總體進度"):
        file_id = str(pdf_path.resolve())
        if file_id in processed_record:
            print(f"🟡 略過已處理：{pdf_path.name}")
            continue

        print(f"\n📄 處理檔案：{pdf_path.name}")
        logging.info(f"處理：{pdf_path.name}")

        try:
            chunks = pdf_processor.process_pdf(pdf_path)
        except Exception as e:
            logging.error(f"PDF 處理失敗 ({pdf_path.name})：{e}")
            continue

        pdf_name_cleaned = pdf_path.stem.strip()
        pdf_output_dir = output_dir / pdf_name_cleaned
        pdf_output_dir.mkdir(parents=True, exist_ok=True)

        vector_store = VectorStore()  # ✅ 每一份 PDF 使用新 index

        for chunk_text, raw_meta in tqdm(chunks, desc="🔹 分段與巾入", leave=False):
            enriched = metadata_handler.enrich_metadata(raw_meta, chunk_text)
            enriched["text"] = chunk_text

            try:
                vector = get_embedding(chunk_text)
                vector_store.add_vectors([vector], [enriched])
            except Exception as e:
                logging.error(f"向量巾入失敗 ({pdf_path.name})：{e}")

        try:
            vector_store.save(pdf_output_dir)
            processed_record[file_id] = {"filename": pdf_path.name}
            save_processed_record(record_file, processed_record)
        except Exception as e:
            logging.error(f"儲存向量失敗 ({pdf_path.name})：{e}")

    print("✅ 建置完成！")
    logging.info("=== 建置完成 ===")

if __name__ == "__main__":
    main()