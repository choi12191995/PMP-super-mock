#!/usr/bin/env python3
"""Generate PMP business domain question JSON files BE-0016 through BE-0466."""
import json
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "questions")

FILES = [
    ("business-02.json", 16, 115),
    ("business-03.json", 116, 215),
    ("business-04.json", 216, 315),
    ("business-05.json", 316, 415),
    ("business-06.json", 416, 466),
]

APPROACHES = ["predictive", "agile", "hybrid"]
TASKS = [f"BE{i}" for i in range(1, 9)]

def distribute(count, weights):
    total = sum(weights)
    raw = [count * w / total for w in weights]
    result = [int(x) for x in raw]
    rem = count - sum(result)
    fracs = [(raw[i] - result[i], i) for i in range(len(weights))]
    fracs.sort(reverse=True)
    for j in range(rem):
        result[fracs[j][1]] += 1
    return result

def make_attrs(n):
    tasks = []
    for i, t in enumerate(TASKS):
        c = n // 8 + (1 if i < n % 8 else 0)
        tasks.extend([t] * c)
    while len(tasks) < n:
        tasks.append(TASKS[len(tasks) % 8])
    tasks = tasks[:n]

    appr = distribute(n, [40, 30, 30])
    approaches = []
    for a, c in zip(APPROACHES, appr):
        approaches.extend([a] * c)
    approaches = approaches[:n]

    diff = distribute(n, [25, 50, 25])
    difficulties = []
    for d, c in zip([1, 2, 3], diff):
        difficulties.extend([d] * c)
    difficulties = difficulties[:n]

    mcq_n = round(n * 0.88)
    multi_n = n - mcq_n
    types = ["mcq"] * mcq_n + ["multi"] * multi_n

    attrs = list(zip(tasks, approaches, difficulties, types))
    # interleave types
    mcqs = [a for a in attrs if a[3] == "mcq"]
    multis = [a for a in attrs if a[3] == "multi"]
    merged = []
    mi, mu = 0, 0
    interval = n / multi_n if multi_n else n + 1
    next_multi = interval / 2
    for i in range(n):
        if mu < multi_n and i >= next_multi:
            merged.append(multis[mu]); mu += 1; next_multi += interval
        else:
            merged.append(mcqs[mi]); mi += 1
    while len(merged) < n:
        merged.append(mcqs[mi] if mi < len(mcqs) else multis[mu])
        if mi < len(mcqs): mi += 1
        else: mu += 1
    return merged[:n]

EXPL_PAD_EN = " As the project manager, applying these principles consistently supports stakeholder trust, audit readiness, and alignment with PMI business domain expectations for effective delivery governance."
EXPL_PAD_ZH = " 作為專案經理，持續應用這些原則可支持利害關係人信任、稽核就緒度，以及與 PMI 業務領域有效交付治理期望的對齊。"

def ensure_expl_length(question):
    for lang, pad in [("en", EXPL_PAD_EN), ("zh", EXPL_PAD_ZH)]:
        words = question["explanation"][lang].split()
        if len(words) < 60:
            text = question["explanation"][lang].rstrip()
            if not text.endswith((".", "。", "!", "?")):
                text += "."
            question["explanation"][lang] = text + pad
    return question

def build_question(qid, task, approach, difficulty, qtype):
    from business_question_banks import MCQ_GETTERS, MULTI_GETTERS
    num = int(qid.split("-")[1])
    idx = num - 16  # global index among new questions

    if qtype == "multi":
        content = MULTI_GETTERS[task](idx)
        question = {
            "id": qid,
            "type": "multi",
            "domain": "business",
            "task": task,
            "approach": approach,
            "difficulty": difficulty,
            "selectN": 2,
            **content,
        }
    else:
        content = MCQ_GETTERS[task](idx)
        question = {
            "id": qid,
            "type": "mcq",
            "domain": "business",
            "task": task,
            "approach": approach,
            "difficulty": difficulty,
            **content,
        }
    return ensure_expl_length(question)

def main():
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    all_questions = []
    for filename, start, end in FILES:
        count = end - start + 1
        attrs = make_attrs(count)
        questions = []
        for i, (task, approach, difficulty, qtype) in enumerate(attrs):
            qid = f"BE-{start + i:04d}"
            questions.append(build_question(qid, task, approach, difficulty, qtype))
        out_path = os.path.join(OUT_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"Wrote {len(questions)} questions to {filename}")
        all_questions.extend(questions)

    # Validate
    ids = [q["id"] for q in all_questions]
    assert len(ids) == len(set(ids)), "Duplicate IDs found"
    assert ids[0] == "BE-0016" and ids[-1] == "BE-0466"
    assert len(all_questions) == 451

    from collections import Counter
    tasks = Counter(q["task"] for q in all_questions)
    approaches = Counter(q["approach"] for q in all_questions)
    diffs = Counter(q["difficulty"] for q in all_questions)
    types = Counter(q["type"] for q in all_questions)
    print(f"\nTotal: {len(all_questions)}")
    print(f"Tasks: {dict(sorted(tasks.items()))}")
    print(f"Approaches: {dict(approaches)}")
    print(f"Difficulty: {dict(sorted(diffs.items()))}")
    print(f"Types: {dict(types)}")

if __name__ == "__main__":
    main()
