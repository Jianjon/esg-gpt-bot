from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()

# 測試 OpenAI API 金鑰
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print("✅ OpenAI API 金鑰已正確設定")
    print(f"金鑰前 8 位：{api_key[:8]}...")
else:
    print("❌ OpenAI API 金鑰未設定") 