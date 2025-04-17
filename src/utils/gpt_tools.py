# src/utils/gpt_tools.py

from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict
from src.utils.message_builder import build_chat_messages
import inspect
import streamlit as st

# ✅ 可選用：啟用 RAG 段落補充
USE_RAG = os.getenv("USE_RAG", "false").lower() == "true"
if USE_RAG:
    try:
        from src.utils.rag_retriever import RAGRetriever
    except ImportError:
        print("⚠️ 啟用 USE_RAG 但找不到 rag_retriever，自動關閉 RAG 功能")
        USE_RAG = False

# 載入環境變數
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key, timeout=20)  # ✅ 建議加上 timeout 保護

def call_gpt(
    prompt: str,
    question_text: str = "",
    learning_goal: str = "",
    chat_history: List[Dict[str, str]] = None,
    industry: str = "",
    rag_doc: str = None,
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.4
) -> str:
    """
    呼叫 GPT 模型，整合問題脈絡與歷史記憶給出回答
    可選用 RAG 模式補充段落背景（需環境變數 USE_RAG=true）
    """
    try:
        rag_context = ""
        if USE_RAG and rag_doc:
            retriever = RAGRetriever()
            rag_context = retriever.get_context(prompt, doc_folder=rag_doc)

        # 組合 messages
        messages = build_chat_messages(
            prompt=prompt,
            question_text=question_text,
            learning_goal=learning_goal,
            chat_history=chat_history,
            industry=industry
        )

        # 插入 RAG 段落（若有）
        if rag_context and messages:
            rag_block = f"以下是輔助參考段落（來自文獻）：\n{rag_context}"
            if messages[0]["role"] == "system":
                messages[0]["content"] += f"\n\n{rag_block}"
            else:
                messages.insert(0, {"role": "system", "content": rag_block})

        # ✅ 印出實際送出的內容（最多前 100 字）
        print("🧪 [call_gpt] 實際送出的 messages：")
        for msg in messages:
            print(f"{msg['role']}: {msg['content'][:100]}...")

        # 呼叫 OpenAI GPT
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=700
        )

        content = response.choices[0].message.content.strip()
        if not content:
            print("⚠️ GPT 回傳為空")
            return "⚠️ AI 回覆為空，請稍後再試。"

        return content

    except Exception as e:
        print(f"⚠️ GPT 回應錯誤：{e}")
        st.warning(f"⚠️ 無法取得 AI 回覆，請稍後再試：{e}")
        return f"⚠️ 無法取得 AI 回覆，請稍後再試：{e}"

# ✅ 確認來源與是否正確載入
print("✅ call_gpt 被載入了！來源：", inspect.getfile(call_gpt))
