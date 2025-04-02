class AnswerSession:
    def __init__(self, user_id: str, question_set: list, stage: str = 'survey'):
        self.user_id = user_id
        self.stage = stage  # 'basic' 或 'advanced'
        self.question_set = question_set  # 問題需包含 id, text, options, type
        self.current_index = 0
        self.responses = []  # 記錄所有回答
        self.finished = False

    def get_current_question(self):
        if self.current_index < len(self.question_set):
            return self.question_set[self.current_index]
        else:
            self.finished = True
            return None

    def submit_response(self, response):
        question = self.get_current_question()
        if question is None:
            return {"error": "No more questions."}

        # 檢查格式
        if question["type"] == "single" and not isinstance(response, str):
            return {"error": "Single-choice question requires a string response."}
        elif question["type"] == "multiple" and not isinstance(response, list):
            return {"error": "Multiple-choice question requires a list of responses."}

        # 記錄回應
        self.responses.append({
            "question_id": question["id"],
            "question_text": question["text"],
            "user_response": response,
            "question_type": question["type"],
            "topic": question.get("topic", "未分類")
        })
        self.current_index += 1
        return {"submitted": True, "next_question": self.get_current_question()}

    def is_finished(self):
        return self.finished

    def get_progress(self):
        return {
            "answered": len(self.responses),
            "total": len(self.question_set),
            "percent": round(len(self.responses) / len(self.question_set) * 100)
        }

    def get_topic_progress(self):
        topic_count = {}
        for q in self.question_set:
            topic = q.get("topic", "未分類")
            topic_count[topic] = topic_count.get(topic, 0) + 1

        topic_done = {}
        for r in self.responses:
            topic = r.get("topic", "未分類")
            topic_done[topic] = topic_done.get(topic, 0) + 1

        return {
            topic: {
                "answered": topic_done.get(topic, 0),
                "total": total
            }
            for topic, total in topic_count.items()
        }

    def get_summary(self, company_baseline=None):
        summary = {
            "user_id": self.user_id,
            "stage": self.stage,
            "total_questions": len(self.question_set),
            "responses": self.responses
        }
        if company_baseline:
            summary["comparison"] = self._compare_with_baseline(company_baseline)
        return summary

    def _compare_with_baseline(self, baseline):
        comparison = []
        for resp in self.responses:
            qid = resp["question_id"]
            baseline_resp = baseline.get(qid, "未知")
            match = resp["user_response"] == baseline_resp
            comparison.append({
                "question_id": qid,
                "question_text": resp.get("question_text", ""),
                "user_response": resp["user_response"],
                "company_response": baseline_resp,
                "match": match
            })
        return comparison
