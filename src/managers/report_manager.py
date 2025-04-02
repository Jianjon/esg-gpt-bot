# managers/report_manager.py

class ReportManager:
    def __init__(self, summary_data: dict):
        """
        接收由 AnswerSession.get_summary() 傳回的資料。
        """
        self.summary = summary_data

    def generate_text_report(self):
        """
        生成純文字格式報告（可印出或儲存成 .txt）。
        """
        lines = []
        lines.append(f"📋 使用者報告 - User ID: {self.summary['user_id']}")
        lines.append(f"問卷階段：{self.summary['stage']}")
        lines.append(f"總題數：{self.summary['total_questions']}")
        lines.append("-" * 40)

        for resp in self.summary["responses"]:
            qid = resp["question_id"]
            qtext = resp["question_text"]
            uresp = resp["user_response"]
            uresp_str = ", ".join(uresp) if isinstance(uresp, list) else uresp
            lines.append(f"Q{qid}: {qtext}")
            lines.append(f"👉 回答：{uresp_str}")
            lines.append("")

        if "comparison" in self.summary:
            lines.append("📊 與公司基準比對：")
            for comp in self.summary["comparison"]:
                match_icon = "✅" if comp["match"] == True else "❌" if comp["match"] == False else "❓"
                lines.append(f"Q{comp['question_id']} ➜ {match_icon}")
                lines.append(f"你選的：{comp['user_response']}")
                lines.append(f"公司基準：{comp['company_response']}")
                lines.append("")

        return "\n".join(lines)

    def generate_json_report(self):
        """
        回傳報告為 JSON 格式，可寫入檔案。
        """
        return self.summary
