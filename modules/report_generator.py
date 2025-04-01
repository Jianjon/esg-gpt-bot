def generate_report(responses):
    report = "# ESG 回饋摘要報告\n\n"
    for q in responses:
        report += f"## 問題：{q['question']}\n- 你的答案：{q['answer']}\n- AI 回饋：{q['feedback']}\n\n"
    return report
