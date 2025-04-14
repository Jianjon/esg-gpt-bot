# src/utils/topic_to_rag_map.py
"""
根據題目主題、內容或標籤，對應適合的向量庫（RAG 文件資料夾）名稱。
支援中英文關鍵字，涵蓋 GHG、碳足跡、SBT、ESG、循環經濟等主題。
"""

def get_rag_doc_for_question(question: dict) -> str:
    """
    根據題目內容自動選擇適合的 RAG 文件資料夾名稱
    Args:
        question (dict): 包含 'id', 'text', 'topic', 'tags' 等欄位的題目資料
    Returns:
        str: RAG 使用的向量資料夾名稱（例如：ISO 14064-1）
    """
    qid = question.get("id", "")
    text = question.get("text", "")
    topic = question.get("topic", "")
    tags = question.get("tags", [])
    note = question.get("question_note", "")

    combined_text = f"{text} {topic} {' '.join(tags)} {note}".lower()

    # --- 主題關鍵字對應表（強化版） ---
    mapping_rules = [
        # GHG 排放與盤查
        ("ghg", "ISO 14064-1"),
        ("溫室氣體", "ISO 14064-1"),
        ("排放範疇", "ISO 14064-1"),
        ("範疇一", "ISO 14064-1"),
        ("範疇二", "ISO 14064-1"),
        ("scope 1", "ISO 14064-1"),
        ("scope 2", "ISO 14064-1"),
        ("scope 3", "ISO 14064-1"),
        ("上游排放", "ISO 14064-1"),
        ("邊界劃分", "ISO 14064-1"),
        ("組織界定", "ISO 14064-1"),

        # 碳足跡與生命週期
        ("碳足跡", "ISO 14067"),
        ("產品碳足跡", "ISO 14067"),
        ("life cycle", "ISO 14067"),
        ("lca", "ISO 14067"),
        ("footprint", "ISO 14067"),

        # 碳中和與抵換
        ("碳中和", "ISO 14068-1-2023_1"),
        ("碳權", "ISO 14068-1-2023_1"),
        ("抵換", "ISO 14068-1-2023_1"),
        ("offset", "ISO 14068-1-2023_1"),

        # SBT / Net Zero
        ("sbt", "SBTi-Corporate-Manual"),
        ("science based target", "SBTi-Corporate-Manual"),
        ("net zero", "SBTi_Net-Zero-Standard"),
        ("碳排目標", "SBTi_Net-Zero-Standard"),
        ("減量路徑", "SBTi_Net-Zero-Standard"),
        ("溫控目標", "SBTi_Net-Zero-Standard"),

        # 再生能源
        ("再生能源", "SBTi_Net-Zero-Standard"),
        ("renewable", "SBTi_Net-Zero-Standard"),
        ("re100", "SBTi_Net-Zero-Standard"),

        # 採購與供應鏈
        ("採購", "ISO_20400_2017E"),
        ("永續採購", "ISO_20400_2017E"),
        ("供應商", "UN_SupplyChainRep"),
        ("供應鏈", "UN_SupplyChainRep"),
        ("上游資料", "UN_SupplyChainRep"),

        # 循環經濟
        ("循環", "ISO_FDIS_59004_N"),
        ("資源再利用", "ISO_FDIS_59004_N"),
        ("延長壽命", "ISO_FDIS_59004_N"),
        ("再設計", "ISO_FDIS_59010N"),
        ("reuse", "ISO_FDIS_59004_N"),
        ("recycle", "ISO_FDIS_59004_N"),

        # ESG 框架 / 指標
        ("esg 指標", "STD_ESG_EOSL_Framework_DHL"),
        ("gri", "STD_ESG_EOSL_Framework_DHL"),
        ("tcfd", "STD_ESG_EOSL_Framework_DHL"),
        ("esg report", "STD_ESG_EOSL_Framework_DHL"),

        # 台灣法規
        ("碳盤查", "TW_MOEA_NetZero_actionguide_2024"),
        ("經濟部", "TW_MOEA_NetZero_actionguide_2024"),
        ("驗證", "TW_ghg_verification_guide_2024"),
        ("工業", "TW_kaohsiung_industry_carbon_manual"),
        ("製造業", "TW_manufacturing_carbon_manual"),
        ("金屬", "TW_metal_emission_guide_2030"),

        # 節能減碳
        ("節能", "TW_manufacturing_carbon_manual"),
        ("減碳", "TW_manufacturing_carbon_manual"),
        ("節電", "TW_manufacturing_carbon_manual"),
    ]

    # --- 優先從關鍵字找 ---
    for keyword, folder in mapping_rules:
        if keyword in combined_text:
            return folder

    # --- 再依 ID 開頭判斷模組（fallback） ---
    if qid.startswith("C") or qid.startswith("S"):
        return "ISO 14064-1"
    elif qid.startswith("D"):
        return "ISO 14067"
    elif qid.startswith("R"):
        return "SBTi-Corporate-Manual"
    elif qid.startswith("M"):
        return "ISO_20400_2017E"

    # --- 預設值（可選：None 或某份共通文件） ---
    return "ISO 14064-1"
