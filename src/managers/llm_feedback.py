import openai
import os

# 載入 API 金鑰（建議用環境變數管理）
openai.api_key = os.getenv("OPENAI_API_KEY")

class LLMFeedback:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def generate_feedback(self, question_text, user_response, company_baseline):
        """
        結合題目內容、使用者回答與公司基準，請 GPT 給出診斷建議。
        """
        baseline_str = (
            ", ".join(company_baseline) if isinstance(company_baseline, list)
            else str(company_baseline)
        )
        user_str = (
            ", ".join(user_response) if isinstance(user_response, list)
            else str(user_response)
        )

        prompt = (
            f"ESG 問卷診斷任務：請根據以下題目，分析使用者的回答與公司基準之間的差異，並提出建設性的改進建議。\n"
            f"\n題目：{question_text}"
            f"\n使用者回答：{user_str}"
            f"\n公司基準：{baseline_str}"
            f"\n請用繁體中文輸出一段 50-100 字的診斷建議，語氣要專業但具鼓勵性。"
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ 無法產生 GPT 診斷建議：{str(e)}"
