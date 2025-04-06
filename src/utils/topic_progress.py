import matplotlib.pyplot as plt
from collections import defaultdict

def get_topic_progress(question_set: list, answered_ids: set):
    """
    輸出主題進度圖（長條圖）
    
    question_set: list of question dicts，需含 'id' 與 'topic'
    answered_ids: set of question_id，使用者已回答的題目
    """
    topic_total = defaultdict(int)
    topic_done = defaultdict(int)

    for q in question_set:
        topic = q.get("topic", "未分類")
        qid = q["id"]
        topic_total[topic] += 1
        if qid in answered_ids:
            topic_done[topic] += 1

    topics = list(topic_total.keys())
    total_list = [topic_total[t] for t in topics]
    done_list = [topic_done[t] for t in topics]
    percent_list = [round(done / total * 100, 1) if total else 0 for done, total in zip(done_list, total_list)]

    # --- 畫圖 ---
    fig, ax = plt.subplots(figsize=(6, 0.5 * len(topics)))
    bars = ax.barh(topics, percent_list, color="#4CAF50")

    for i, (done, total, pct) in enumerate(zip(done_list, total_list, percent_list)):
        ax.text(pct + 1, i, f"{done}/{total}（{pct}%）", va="center", fontsize=10)

    ax.set_xlim(0, 100)
    ax.set_xlabel("完成百分比 (%)")
    ax.set_title("ESG 主題完成進度")
    plt.tight_layout()

    return fig
