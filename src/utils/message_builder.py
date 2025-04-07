# src/utils/message_builder.py
from typing import List, Dict

def build_chat_messages(
    prompt: str,
    question_text: str = "",
    learning_goal: str = "",
    chat_history: List[Dict[str, str]] = None,
    industry: str = "",
    system_role: str = ""
) -> List[Dict[str, str]]:

    # 根據產業動態設定角色語氣
    industry_prompt = f"你正在協助一家屬於「{industry}」的企業進行 ESG 問卷與碳盤查診斷。" if industry else ""
    
    if not system_role:
        system_role = (
            f"{industry_prompt} 你是一位專業的 ESG 顧問，擅長逐題引導企業理解碳盤查要點，語氣親切且能協助使用者釐清重點。\n"
            "請根據題目脈絡與提問，提供 **實用、簡潔、帶有同理心** 的建議，並符合以下風格：\n"
            "1. 儘量使用 **條列式** 說明具體做法與觀念。\n"
            "2. 在回答最後加入 **鼓勵性語氣**，讓使用者感覺被支持。\n"
            "3. 若適合，可補充 **實務案例** 或常見作法。\n"
            "4. 用 **加粗字** 強調關鍵詞。\n"
            "5. 避免艱澀語言，要像顧問和學員對談般自然。\n"
            "6. 若使用者已提問五輪，請幫忙**總結重點**，並建議進入下一題。"
        )

    messages = [{"role": "system", "content": system_role}]

    # ➤ 若對話數量達五輪，先進行總結並附上提醒
    if chat_history and len(chat_history) >= 5:
        summary_lines = []
        for i, turn in enumerate(chat_history[-5:], 1):
            summary_lines.append(f"【第{i}輪】\n使用者：{turn.get('user', '')}\nAI：{turn.get('gpt', '')}\n")

        summary_context = "\n".join(summary_lines)

        messages.append({
            "role": "system",
            "content": "您已與使用者進行多輪互動，請協助總結對話重點，並以親切語氣鼓勵他進入下一題。。"
        })

        messages.append({
            "role": "user",
            "content": (
                f"這題為：「{question_text}」\n"
                f"學習目標：「{learning_goal}」\n"
                f"以下是對話紀錄：\n{summary_context}\n\n"
                "請用條列式總結本題重點，並建議我進入下一題。。"
            )        })

    else:
        # 未滿 5 輪則照常建立完整上下文對話
        if chat_history:
            for turn in chat_history:
                if "user" in turn and turn["user"]:
                    messages.append({"role": "user", "content": turn["user"]})
                if "gpt" in turn and turn["gpt"]:
                    messages.append({"role": "assistant", "content": turn["gpt"]})

        # 加入當前提問
        if question_text or learning_goal:
            user_prompt = (
                f"這題是：「{question_text}」\n"
                f"學習目標是：「{learning_goal}」\n"
                f"使用者新提出的問題是：「{prompt}」\n\n"
                "請根據上下文與提問，給予清楚具體的建議，必要時補充碳盤查對於用戶的可執行行動方針。"
            )
        else:
            user_prompt = prompt

        messages.append({"role": "user", "content": user_prompt.strip()})

    return messages
