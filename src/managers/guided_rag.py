# guided_rag.py
from typing import List, Tuple, Dict
import streamlit as st
from vector_builder.vector_store import VectorStore  # ✅ 替換為新的 HuggingFace VectorStore

class GuidedRAG:
    def __init__(self, vector_path="data/vector_output_hf/", model="gpt-4"):
        self.vector_store = VectorStore()
        self.vector_store.load(vector_path)
        self.model = model
        self.max_turns = 3

    def search_related_chunks(self, question: str, top_k: int = 5) -> List[Dict]:
        return self.vector_store.search(question, top_k=top_k)

    def build_prompt(self, user_question: str, context_chunks: List[Dict], turn: int, tone: str = "gentle") -> List[Dict]:
        context_text = "\n\n".join([chunk.get('text', '（無段落資料）') for chunk in context_chunks])

        tone_styles = {
            "gentle": "請使用溫和鼓勵的語氣來說明問題。",
            "professional": "請使用邏輯清晰、專業的語氣來說明問題。",
            "creative": "請使用有創意、跳脫框架的語氣來啟發使用者。"
        }
        tone_instruction = tone_styles.get(tone, "")

        system_prompt = f"""
你是一位專業的永續顧問，正在引導客戶完成 ESG 問卷。
{tone_instruction}
根據以下背景資料，請幫助使用者理解問題，並試著引導對方選出適當的選項。
若使用者說「不知道」或無法回答，請進一步說明或提供範例幫助其理解。

以下是相關資料：\n{context_text}
"""

        user_prompt = f"這是使用者的問題（第 {turn} 輪）：{user_question}\n\n請提供清楚解釋，最後提出 2 到 3 個可能的選項，或鼓勵使用者自行輸入看法。"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def ask(self, user_question: str, history: List[Tuple[str, str]], turn: int = 1) -> Tuple[str, List[Dict]]:
        chunks = self.search_related_chunks(user_question)
        tone = st.session_state.get("preferred_tone", "gentle")
        messages = self.build_prompt(user_question, chunks, turn, tone=tone)

        try:
            import openai  # ✅ 僅於需要時載入，避免未使用仍導入錯誤
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            answer = response["choices"][0]["message"]["content"].strip()
            return answer, chunks
        except Exception as e:
            return f"❌ 查詢失敗：{str(e)}", []

    def query(self, question: str) -> str:
        answer, _ = self.ask(user_question=question, history=[], turn=1)
        return answer