# sessions/answer_session.py

class AnswerSession:
    def __init__(self, user_id: str, question_set: list, stage: str = 'survey'):
        """
        初始化一個問卷會話。

        參數:
        - user_id: 使用者識別碼
        - question_set: 題目清單，每題需包含 id, text, options, type（'single' 或 'multiple'）
        - stage: 問卷階段名稱，預設為 'survey'
        """
        self.user_id = user_id
        self.stage = stage
        self.question_set = question_set
        self.current_index = 0
        self.responses = []
        self.finished = False

    def get_current_question(self):
        """
        回傳目前題目，若問卷已完成則回傳 None。
        """
        if self.current_index < len(self.question_set):
            return self.question_set[self.current_index]
        else:
            self.finished = True
            return None

    def submit_response(self, response):
        """
        提交使用者回應，並自動前進到下一題。

        response: 若為單選，需為 string；若為複選，需為 list。
        """
        question = self.get_current_question()
        if question is None:
            return {"error": "No more questions."}

        # 類型驗證
        if question["type"] == "single" and not isinstance(response, str):
            return {"error": "單選題需為單一字串選項。"}
        elif question["type"] == "multiple" and not isinstance(response, list):
            return {"error": "複選題需為選項列表。"}

        # 紀錄回應
        self.responses.append({
            "question_id": question["id"],
            "question_text": question["text"],
            "user_response": response,
            "question_type": question["type"]
        })

        self.current_index += 1
        return {"submitted": True, "next_question": self.get_current_question()}

    def is_finished(self):
        """
        檢查問卷是否完成。
        """
        return self.finished

    def get_summary(self, company_baseline=None):
        """
        回傳使用者回應摘要，可選擇是否對照公司 baseline。

        company_baseline: 字典格式 {question_id: baseline_response}
        """
        summary = {
            "user_id": self.user_id,
            "stage": self.stage,
            "total_questions": len(self.question_set),
            "responses": self.responses
        }

        if company_baseline:
            summary["comparison"] = self._compare_with_baseline(company_baseline)

        return summary

    def _compare_with_baseline(self, baseline: dict):
        """
        將使用者回應與 baseline 做比對，傳回差異清單。
        """
        comparison = []

        for resp in self.responses:
            qid = resp["question_id"]
            user_resp = resp["user_response"]
            baseline_resp = baseline.get(qid, None)

            if baseline_resp is None:
                match = "未知"
            elif resp["question_type"] == "single":
                match = (user_resp == baseline_resp)
            elif resp["question_type"] == "multiple":
                match = set(user_resp) == set(baseline_resp)
            else:
                match = "格式錯誤"

            comparison.append({
                "question_id": qid,
                "question_text": resp["question_text"],
                "user_response": user_resp,
                "company_response": baseline_resp,
                "match": match
            })

        return comparison
