import streamlit as st

# src/managers/profile_manager.py

# src/managers/profile_manager.py

# src/managers/profile_manager.py

# src/managers/profile_manager.py

def get_user_profile(user_id: str = "default") -> dict:
    """
    模擬取得使用者基本資料，後續可改為連接資料庫或 session。
    """
    return {
        "user_id": user_id,
        "user_name": "Jon",
        "industry": "餐飲業",
        "learning_stage": "beginner",  # beginner / intermediate
        "carbon_knowledge": "了解一點點",
        "has_cf_need": True,
        "esg_motivation": ["提升公司形象", "教育推廣"],
    }



