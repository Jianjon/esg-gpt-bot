from managers.llm_feedback import LLMFeedback

class FeedbackManager:
    def __init__(self, comparisons, use_gpt=False):
        self.comparisons = comparisons
        self.use_gpt = use_gpt
        self.llm_feedback = LLMFeedback() if use_gpt else None

    def generate_feedback(self):
        feedback_list = []

        for item in self.comparisons:
            qid = item["question_id"]
            question = item["question_text"]
            user_answer = item["user_response"]
            company_answer = item["company_response"]
            match = item["match"]

            # ✅ 傳統建議邏輯（必有）
            if match == True:
                suggestion = f"✅ 貴公司在「{question}」方面已與基準一致，請持續維持現行做法。"
            elif match == False:
                suggestion = (
                    f"⚠️ 在「{question}」這題，您的回應與公司基準不同，建議回顧現行做法是否落實。"
                )
            else:
                suggestion = f"❓「{question}」目前無可比較基準，建議先建立 baseline 再評估。"

            # 🔁 加入 GPT 診斷建議（選配）
            if self.use_gpt and self.llm_feedback:
                gpt_suggestion = self.llm_feedback.generate_feedback(
                    question_text=question,
                    user_response=user_answer,
                    company_baseline=company_answer
                )
                suggestion += f"\n🤖 GPT 建議：{gpt_suggestion}"

            feedback_list.append({
                "question_id": qid,
                "feedback": suggestion
            })

        return feedback_list

    def generate_overall_feedback(self):
        total = len(self.comparisons)
        matched = sum(1 for i in self.comparisons if i["match"] == True)
        unmatched = sum(1 for i in self.comparisons if i["match"] == False)

        if total == 0:
            return "⚠️ 尚無比對結果，無法產出總體診斷建議。"

        if matched == total:
            return "🎉 您的作答與公司基準完全一致，展現出良好的永續認知與實踐一致性！"
        elif unmatched / total > 0.5:
            return "⚠️ 有超過一半的回答與公司基準不一致，建議進行內部教育訓練或流程盤點。"
        else:
            return "👍 大部分回答與基準一致，部分差異可以作為改進契機。"
