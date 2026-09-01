import json
# from app.services.rag import retrieve
from pathlib import Path
from app.services.rag import retrieve_with_rerank as retrieve
TOP_K = 5

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR/ "eval_questions_hard.json",
          "r",
          encoding="utf-8"
    ) as f:
          cases = json.load(f)

hit_1_count = 0
hit_3_count = 0
hit_5_count = 0
rr_sum = 0.0

for case in cases:
    question = case["question"]
    expected_text = case["expected_text"]

    results = retrieve(question, top_k=TOP_K)

    correct_rank = None

    for rank, hit in enumerate(results, start=1):
        if expected_text in hit["text"]:
            correct_rank = rank
            break

    if correct_rank is not None:
        if correct_rank <= 1 :
            hit_1_count += 1
        if correct_rank <= 3 :
            hit_3_count += 1
        if correct_rank <= 5:
            hit_5_count +=1
        rr = 1 / correct_rank
    else:
        rr = 0.0

    rr_sum += rr

    print("=" * 70)
    print("问题：", question)
    print("正确片段关键文本：", expected_text)
    print("正确片段排名：", correct_rank)
    print("Hit@1:", 1 if correct_rank is not None and correct_rank <= 1 else 0)
    print("Hit@3:", 1 if correct_rank is not None and correct_rank <= 3 else 0)
    print("Hit@5:", 1 if correct_rank is not None and correct_rank <= 5 else 0)
    print("RR：", rr)

total = len(cases)
hit_at_1 = hit_1_count / total
hit_at_3 = hit_3_count / total
hit_at_5 = hit_5_count / total
mrr = rr_sum / total

print("\n" + "#" * 70)
print("题目数量：", total)
print(f"Hit@1：{hit_at_1:.4f}")
print(f"Hit@3：{hit_at_3:.4f}")
print(f"Hit@5：{hit_at_5:.4f}")
print(f"MRR：{mrr:.4f}")
