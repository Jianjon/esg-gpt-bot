from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict
from src.utils.message_builder import build_chat_messages
import inspect  # ← 加在這裡也可以

# 載入環境變數
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_gpt(
    prompt: str,
    question_text: str = "",
    learning_goal: str = "",
    chat_history: List[Dict[str, str]] = None,
    industry: str = "",
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.4
) -> str:
    """
    呼叫 GPT 模型，整合問題脈絡與歷史記憶給出回答
    """
    try:
        messages = build_chat_messages(prompt, question_text, learning_goal, chat_history, industry=industry)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT 回應錯誤：{e}")
        return "目前無法取得 AI 回覆，請稍後再試。"

# ✅ 把這行移到函式定義之後！
print("✅ call_gpt 被載入了！來源：", inspect.getfile(call_gpt))
