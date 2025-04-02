# 📂 src/__init__.py
# 模組初始化：無需內容，確保 src 為 Python 套件資料夾


# 📁 src/loaders/question_loader.py
"""
讀取所有題庫 CSV，並依據 industry_type 整理為 dict 格式。
提供檢查欄位格式一致性的基本功能。
"""


# 📁 src/parsers/answer_parser.py
"""
解析使用者回答 JSON，轉為內部標準格式：
包含 question_id、report_section、answer_tags 等欄位。
"""


# 📁 src/generators/report_generator.py
"""
依據答題結構資料，從語句模組（Markdown）中擷取段落，
組合為段落式報告（初階分段 + 全文 500 字）。
"""


# 📁 src/renderers/output_formatter.py
"""
將報告內容輸出為 Markdown、純文字、HTML 等格式，
並加入標題、段落註記與時間戳。
"""


# 📁 src/utils/validation.py
"""
驗證題庫欄位格式是否與 schema 對齊。
檢查每題是否有對應語句模組（避免漏段落）。
"""


# 📁 src/ui/cli_runner.py
"""
命令列互動工具，模擬使用者選題、答題、產出報告完整流程。
日後可作為 API 或前端 UI 整合前測試入口。
"""
