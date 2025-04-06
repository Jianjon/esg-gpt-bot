import openai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    呼叫 GPT 模型，根據提供的 prompt 生成回應。
    Params:
        - prompt: 提供給 GPT 的文字提示
        - model: 使用的 GPT 模型（預設為 gpt-3.5-turbo）
    Return:
        - GPT 回應的文字
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位善於解釋 ESG 與碳盤查的顧問型助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("⚠️ GPT 回應錯誤：", e)
        return "系統忙碌中，請稍後再試"