# managers/feedback_manager.py

class FeedbackManager:
    def __init__(self, comparison_data: list):
        """
        傳入由 AnswerSession.get_summary()['comparison'] 傳回的比較資料。
        """
        self.comparison = comparison_data

    def generate_feedback(self):
        """
        根據使用者與 baseline 的差異產生建議（可串接 GPT）。
        """
        feedback_list = []

        for item in self.comparison:
            qid = item["question_id"]
            question = item["question_text"]
            user_answer = item["user_response"]
            company_answer = item["company_response"]
            match = item["match"]

            if match == True:
                suggestion = f"✅ 貴公司在「{question}」方面已與基準一致，請持續維持現行做法。"
            elif match == False:
                suggestion = (
                    f"⚠️ 在「{question}」這一題，您的回應與公司基準不同。\n"
                    f"👉 建議回顧現行做法是否落實，或重新確認策略方向。"
                )
            else:
                suggestion = f"❓「{question}」目前無可比較基準，建議先建立 baseline 再評估。"

            feedback_list.append({
                "question_id": qid,
                "feedback": suggestion
            })

        return feedback_list

    def generate_overall_feedback(self):
        """
        根據整體 match 結果給出總體評語（未來可串 GPT）。
        """
        total = len(self.comparison)
        matched = sum(1 for i in self.comparison if i["match"] == True)
        unmatched = sum(1 for i in self.comparison if i["match"] == False)

        if matched == total:
            return "🎉 您的作答與公司基準完全一致，展現出良好的永續認知與實踐一致性！"
        elif unmatched / total > 0.5:
            return "⚠️ 有超過一半的回答與公司基準不一致，建議進行內部教育訓練或流程盤點。"
        else:
            return "👍 大部分回答與基準一致，部分差異可以作為改進契機。"

