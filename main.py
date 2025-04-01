from modules.question_loader import load_questions
from modules.response_engine import generate_feedback
from modules.report_generator import generate_report

def main():
    questions = load_questions("data/demo_questions.csv")
    responses = []

    for q in questions:
        print(q["text"])
        user_answer = input("你的回答：")
        feedback = generate_feedback(q, user_answer)
        responses.append({
            "question": q["text"],
            "answer": user_answer,
            "feedback": feedback
        })

    report = generate_report(responses)
    print("\n" + report)

if __name__ == "__main__":
    main()
