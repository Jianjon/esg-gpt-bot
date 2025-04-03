"""
Metadata 處理模組
負責處理和擴充 PDF chunks 的 metadata
"""

from pathlib import Path
from typing import Dict, List
import re
import json
import logging

class MetadataHandler:
    def __init__(self):
        # 產業關鍵字對應
        self.industry_keywords = {
            'retail': ['retail', 'shopping', '零售', '商場'],
            'manufacturing': ['manufacturing', 'factory', '製造', '工廠'],
            'technology': ['technology', 'software', '科技', '軟體'],
            'finance': ['banking', 'finance', '金融', '銀行'],
            'energy': ['energy', 'power', '能源', '電力'],
            'healthcare': ['healthcare', 'medical', '醫療', '健康']
        }
        
    def detect_language(self, text: str) -> str:
        """檢測文本語言（簡單實現）"""
        chinese_char_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_char_count = len(text.strip())
        
        if total_char_count == 0:
            return "en"
            
        chinese_ratio = chinese_char_count / total_char_count
        return "zh" if chinese_ratio > 0.1 else "en"
    
    def extract_topic(self, pdf_path: Path, text: str) -> str:
        """從檔案路徑和內容提取主題"""
        # 從路徑提取
        path_parts = pdf_path.parts
        if "international" in path_parts:
            return path_parts[path_parts.index("international") + 1].lower()
        
        # 從檔名和內容關鍵字判斷
        keywords = {
            'sustainability': ['sustainability', 'ESG', '永續', '環境'],
            'climate': ['climate', 'carbon', '氣候', '碳'],
            'governance': ['governance', 'compliance', '治理', '法遵'],
            'social': ['social', 'community', '社會', '社區']
        }
        
        text_lower = text.lower()
        for topic, kws in keywords.items():
            if any(kw.lower() in text_lower or kw.lower() in pdf_path.stem.lower() for kw in kws):
                return topic
                
        return "general"
    
    def extract_industry(self, pdf_path: Path, text: str) -> str:
        """從檔案路徑和內容提取產業類別"""
        if "cases" in pdf_path.parts:
            text_lower = text.lower()
            for industry, keywords in self.industry_keywords.items():
                if any(kw.lower() in text_lower or kw.lower() in pdf_path.stem.lower() for kw in keywords):
                    return industry
        return "cross_industry"
    
    def extract_region(self, pdf_path: Path) -> str:
        """從檔案路徑提取地區"""
        if "taiwan" in pdf_path.parts:
            return "taiwan"
        elif "international" in pdf_path.parts:
            return "global"
        return "unknown"
    
    def enrich_metadata(self, chunk_metadata: Dict, text: str) -> Dict:
        """擴充metadata資訊"""
        pdf_path = Path(chunk_metadata["source"])
        
        # 添加額外metadata
        chunk_metadata.update({
            "main_topic": self.extract_topic(pdf_path, text),
            "industry": self.extract_industry(pdf_path, text),
            "region": self.extract_region(pdf_path),
            "language": self.detect_language(text)
        })
        
        # 移除暫存的text欄位
        if "text" in chunk_metadata:
            del chunk_metadata["text"]
            
        return chunk_metadata
    
    def save_metadata(self, metadata_list: List[Dict], output_path: Path):
        """儲存metadata到JSON檔案"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}") 