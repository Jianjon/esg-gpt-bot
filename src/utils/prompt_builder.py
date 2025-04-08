from src.utils.gpt_tools import call_gpt

def generate_user_friendly_prompt(current_q: dict, user_profile: dict) -> str:
    learning_goal = current_q.get("learning_goal", "")
    question_text = current_q.get("text", "")
    question_note = current_q.get("question_note", "")

    # 取前導問卷的幾個核心資訊
    role = user_profile.get("q4", "")
    motivation = user_profile.get("q2", "")
    experience = user_profile.get("q5", "")

    prompt = f"""
你是一位專業 ESG 顧問，正在引導一位使用者完成 ESG 問卷。
請根據以下資料，用親切、口語化、精準的方式生成一段約 100 字左右的顧問引導語，說明這題為什麼重要、要怎麼思考。

【使用者背景】
- 角色：{role}
- 動機：{motivation}
- 經驗：{experience}

【題目資訊】
- 學習目標：{learning_goal}
- 題目內容：{question_text}
- 題目說明：{question_note}

請用一段自然對話式口吻引導他開始作答，語氣要像顧問與客戶對話。
    """

    reply = call_gpt(prompt, temperature=0.7)
    return reply


def build_learning_prompt(user_profile: dict, question: dict, user_answer: list | str) -> str:
    name = user_profile.get("user_name", "使用者")
    company = user_profile.get("company_name", "貴公司")
    industry = user_profile.get("industry", "某產業")
    q_text = question.get("text", "")
    q_note = question.get("question_note", "")
    learning_goal = question.get("learning_goal", "")
    answer_display = ", ".join(user_answer) if isinstance(user_answer, list) else user_answer

    prompt = f"""
您好，我是一位企業使用者，來自「{company}」（產業：{industry}）。

在 ESG 問卷中，我剛剛回答了這題：
👉 題目：{q_text}
👉 題目說明：{q_note}
👉 我的作答為：{answer_display}

請依據這個背景，幫我針對以下幾個面向進行簡單教學引導（目標是：{learning_goal}）：

1. 📘 用簡單方式解釋這題的重點知識
2. 🧠 評估我的作答是否正確，有哪些補充建議？
3. 💡 提出企業常見的處理方式或具體實務建議
4. 🚀 給我一點鼓勵，並建議下一步可以學什麼

請用條列式整理，每段開頭加上主題小圖示與黑體字，簡明但有啟發性。謝謝！
"""
    return prompt.strip()

