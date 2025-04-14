from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict
from src.utils.message_builder import build_chat_messages
from src.utils.rag_retriever import RAGRetriever  # ✅ 新增：RAG 向量補充模組
import inspect
import streamlit as st  # ✅ 若用在 Streamlit 畫面中除錯提示

# 載入環境變數
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def call_gpt(
    prompt: str,
    question_text: str = "",
    learning_goal: str = "",
    chat_history: List[Dict[str, str]] = None,
    industry: str = "",
    rag_doc: str = None,  # ✅ 新增：指定向量文件（資料夾）名稱
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.4
) -> str:
    """
    呼叫 GPT 模型，整合問題脈絡與歷史記憶給出回答
    可選用 RAG 模式補充段落背景
    """
    try:
        rag_context = ""
        if rag_doc:
            retriever = RAGRetriever()
            rag_context = retriever.get_context(prompt, doc_folder=rag_doc)

        # 檢查 prompt 與上下文訊息
        messages = build_chat_messages(
            prompt=prompt,
            question_text=question_text,
            learning_goal=learning_goal,
            chat_history=chat_history,
            industry=industry
        )

        # 如果有 RAG 段落補充，插入在第一則 system message 後
        if rag_context and len(messages) > 0:
            rag_block = f"以下是輔助參考段落（來自文獻）：\n{rag_context}"
            if messages[0]["role"] == "system":
                messages[0]["content"] += f"\n\n{rag_block}"
            else:
                messages.insert(0, {"role": "system", "content": rag_block})

        print("🧪 [call_gpt] 實際送出的 messages：")
        for msg in messages:
            print(f"{msg['role']}: {msg['content'][:100]}...")

        # 呼叫 OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=700
        )

        content = response.choices[0].message.content.strip()

        if not content:
            print("⚠️ GPT 回傳為空")
        return content

    except Exception as e:
        print(f"⚠️ GPT 回應錯誤：{e}")
        st.warning(f"⚠️ 無法取得 AI 回覆，請稍後再試：{e}")
        return "目前無法取得 AI 回覆，請稍後再試。"

# ✅ Debug log，確認來源檔案與是否載入
print("✅ call_gpt 被載入了！來源：", inspect.getfile(call_gpt))