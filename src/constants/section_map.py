# 題目章節對應表（可供側邊欄、摘要報告、章節進度條等功能使用）

STAGE_MAP = {
    "basic": "beginner",
    "advanced": "intermediate"
}

MANUAL_SECTION_QUESTIONS = {
    "ESG 教學導入（教學前導）": [
        {"id": "C000", "title": "什麼是溫室氣體？", "difficulty": "beginner"},
        {"id": "C001", "title": "碳盤查是什麼？", "difficulty": "beginner"},
        {"id": "C002", "title": "碳足跡是什麼？", "difficulty": "beginner"},
        {"id": "C003", "title": "誰需要做碳盤查或碳足跡？", "difficulty": "beginner"},
        {"id": "C004", "title": "碳盤查與碳足跡的用途？", "difficulty": "beginner"}
    ],

    "邊界設定與組織資訊": [
        {"id": "B001", "title": "組織範圍", "difficulty": "beginner"},
        {"id": "B002", "title": "盤查範圍", "difficulty": "beginner"},
        {"id": "B003", "title": "企業關聯", "difficulty": "beginner"},
        {"id": "B004", "title": "永續人員", "difficulty": "beginner"},
        {"id": "B005", "title": "減排政策", "difficulty": "beginner"},
        {"id": "B006", "title": "減排目標", "difficulty": "beginner"},
        {"id": "B007", "title": "報告需求", "difficulty": "beginner"},
        {"id": "B008", "title": "盤查挑戰", "difficulty": "intermediate"},
        {"id": "B009", "title": "碳訓練經驗", "difficulty": "intermediate"},
        {"id": "B010", "title": "負責人與團隊", "difficulty": "intermediate"}
    ],

    "排放源辨識與確認": [
        {"id": "S001", "title": "排放主要來源", "difficulty": "beginner"},
        {"id": "S002", "title": "能源使用類型", "difficulty": "beginner"},
        {"id": "S003", "title": "燃料燃燒情形", "difficulty": "beginner"},
        {"id": "S004", "title": "車隊與物流", "difficulty": "beginner"},
        {"id": "S005", "title": "原物料採購", "difficulty": "intermediate"},
        {"id": "S006", "title": "包裝材料", "difficulty": "intermediate"},
        {"id": "S007", "title": "廢棄物處理", "difficulty": "intermediate"},
        {"id": "S008", "title": "用水與污水", "difficulty": "intermediate"},
        {"id": "S009", "title": "特殊排放源", "difficulty": "intermediate"},
        {"id": "S010", "title": "排放因子來源", "difficulty": "intermediate"},
        {"id": "S011", "title": "排放計算方式", "difficulty": "intermediate"},
        {"id": "S012", "title": "減排實施計畫", "difficulty": "intermediate"},
        {"id": "S013", "title": "減排監控方法", "difficulty": "intermediate"},
        {"id": "S014", "title": "持續改進機制", "difficulty": "intermediate"}
    ],

    "數據收集方式與能力": [
        {"id": "D001", "title": "數據頻率來源", "difficulty": "beginner"},
        {"id": "D002", "title": "電力紀錄", "difficulty": "beginner"},
        {"id": "D003", "title": "燃料紀錄", "difficulty": "beginner"},
        {"id": "D004", "title": "物流紀錄", "difficulty": "beginner"},
        {"id": "D005", "title": "採購紀錄", "difficulty": "beginner"},
        {"id": "D006", "title": "廢棄物數據", "difficulty": "intermediate"},
        {"id": "D007", "title": "數據模板", "difficulty": "intermediate"},
        {"id": "D008", "title": "數據品質", "difficulty": "intermediate"},
        {"id": "D009", "title": "內部稽核", "difficulty": "intermediate"},
        {"id": "D010", "title": "技術工具", "difficulty": "intermediate"},
        {"id": "D011", "title": "電子紀錄", "difficulty": "intermediate"},
        {"id": "D012", "title": "紀錄責任人", "difficulty": "intermediate"},
        {"id": "D013", "title": "最佳實踐", "difficulty": "intermediate"},
        {"id": "D014", "title": "系統備份", "difficulty": "intermediate"},
        {"id": "D015", "title": "資料收集 SOP", "difficulty": "intermediate"},
        {"id": "D016", "title": "定期審核", "difficulty": "intermediate"}
    ],

    "內部管理與SOP現況": [
        {"id": "M001", "title": "報告內容格式", "difficulty": "intermediate"},
        {"id": "M002", "title": "第三方驗證", "difficulty": "intermediate"},
        {"id": "M003", "title": "文件編號", "difficulty": "intermediate"},
        {"id": "M004", "title": "版本控制", "difficulty": "intermediate"},
        {"id": "M005", "title": "存儲方式", "difficulty": "intermediate"},
        {"id": "M006", "title": "審批流程", "difficulty": "intermediate"},
        {"id": "M007", "title": "存取權限", "difficulty": "intermediate"},
        {"id": "M008", "title": "存檔期限", "difficulty": "intermediate"},
        {"id": "M009", "title": "文件案例", "difficulty": "intermediate"},
        {"id": "M010", "title": "碳制度建立", "difficulty": "intermediate"},
        {"id": "M011", "title": "內管建議", "difficulty": "intermediate"}
    ],

    "報告需求與後續行動": [
        {"id": "R001", "title": "員工訓練需求", "difficulty": "intermediate"},
        {"id": "R002", "title": "訓練頻率", "difficulty": "intermediate"},
        {"id": "R003", "title": "內部溝通", "difficulty": "intermediate"},
        {"id": "R004", "title": "合規要求", "difficulty": "intermediate"},
        {"id": "R005", "title": "資源分配", "difficulty": "intermediate"},
        {"id": "R006", "title": "合規檢查", "difficulty": "intermediate"},
        {"id": "R007", "title": "文件預算", "difficulty": "intermediate"},
        {"id": "R008", "title": "文件更新頻率", "difficulty": "intermediate"},
        {"id": "R009", "title": "碳績效檢討", "difficulty": "intermediate"},
        {"id": "R010", "title": "績效指標", "difficulty": "intermediate"},
        {"id": "R011", "title": "歷史趨勢分析", "difficulty": "intermediate"},
        {"id": "R012", "title": "減碳策略建議", "difficulty": "intermediate"},
        {"id": "R013", "title": "對外溝通", "difficulty": "intermediate"},
        {"id": "R014", "title": "產業對標分析", "difficulty": "intermediate"},
        {"id": "R015", "title": "下一步建議", "difficulty": "intermediate"}
    ]
}
