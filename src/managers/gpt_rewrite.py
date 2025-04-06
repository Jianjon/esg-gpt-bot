"""
GPT 題目自然語氣改寫器模組：將問卷題目轉換為適合對話語氣。
支援基本句型轉換與 GPT 模型增強改寫。
"""

import openai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_rewrite(question_text: str) -> str:
    """簡單句型轉換，不使用 GPT"""
    if "是否" in question_text:
        return f"我們來聊聊：{question_text.replace('是否', '您目前有沒有')}"
    elif question_text.endswith("？"):
        return question_text.replace("？", "呢？")
    return f"請談談您的經驗：{question_text}"


def gpt_rewrite(question_text: str, question_type: str = "single", learning_goal: str = "") -> str:
    """使用 GPT 模型改寫"""
    prompt = f"""
你是一位 ESG 顧問型 AI 助理，目標是將問卷題目改寫為自然、對話式的提問語句。
請使用尊重而親切的語氣，使使用者願意分享真實想法。

題目原文：{question_text}
題目類型：{"單選題" if question_type == "single" else "多選題"}
{"學習目標：" + learning_goal if learning_goal else ""}

請用對話語氣重新提問這個問題：
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位擅長語言引導的 ESG 顧問助手。"},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.5,
            max_tokens=100
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ GPT 改寫失敗：{e}")
        return basic_rewrite(question_text)


def rewrite_question_to_conversational(
    question_text: str,
    question_type: str = "single",
    learning_goal: str = "",
    use_gpt: bool = False
) -> str:
    """
    統一入口：自然語氣改寫器
    Params:
        - question_text: 題目原文
        - question_type: 題型（single/multiple）
        - learning_goal: 學習目標
        - use_gpt: 是否使用 GPT 模型改寫

    Return:
        - 改寫後的自然語氣提問
    """
    if use_gpt:
        return gpt_rewrite(question_text, question_type, learning_goal)
    else:
        return basic_rewrite(question_text)


# ✅ 若直接執行此檔，可進行改寫測試
if __name__ == "__main__":
    sample_q = {
        "text": "您是否有盤點公司各部門的溫室氣體排放來源？",
        "type": "single",
        "learning_goal": "了解排放源辨識的基本步驟"
    }

    gpt_text = rewrite_question_to_conversational(
        question_text=sample_q["text"],
        question_type=sample_q.get("type", "single"),
        learning_goal=sample_q.get("learning_goal", ""),
        use_gpt=True
    )
    print("✅ GPT 改寫結果：\n", gpt_text)
