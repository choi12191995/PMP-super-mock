#!/usr/bin/env python3
"""Shared utilities for procedural PMP question generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "public" / "questions"

APPROACHES = ["predictive", "agile", "hybrid"]
APPROACH_WEIGHTS = [40, 30, 30]
DIFFICULTIES = [1, 2, 3]
DIFF_WEIGHTS = [25, 50, 25]

INDUSTRIES = [
    ("healthcare", "醫療保健", "regional hospital network", "區域醫院體系"),
    ("fintech", "金融科技", "digital banking platform", "數位銀行平台"),
    ("manufacturing", "製造業", "smart factory modernization", "智慧工廠現代化"),
    ("telecom", "電信", "5G infrastructure rollout", "5G 基礎設施部署"),
    ("energy", "能源", "renewable grid expansion", "再生能源電網擴建"),
    ("retail", "零售", "omnichannel commerce program", "全通路商務計畫"),
    ("government", "政府", "digital public services portal", "數位公共服務入口"),
    ("aerospace", "航太", "satellite constellation program", "衛星星座計畫"),
    ("insurance", "保險", "claims processing modernization", "理賠處理現代化"),
    ("logistics", "物流", "warehouse automation initiative", "倉儲自動化計畫"),
    ("education", "教育", "learning management transformation", "學習管理轉型"),
    ("construction", "營造", "infrastructure upgrade program", "基礎設施升級計畫"),
    ("software", "軟體", "enterprise SaaS migration", "企業 SaaS 遷移"),
    ("pharma", "製藥", "clinical trial operations platform", "臨床試驗營運平台"),
    ("transportation", "運輸", "intelligent transit system", "智慧運輸系統"),
]

TEAM_SIZES = [
    ("a co-located team of twelve", "十二人同地團隊"),
    ("a distributed team across four time zones", "跨四時區分散團隊"),
    ("a cross-functional squad of eight", "八人跨職能小隊"),
    ("a program with three vendor teams and internal staff", "含三家廠商與內部人員的計畫"),
    ("a matrix organization with shared resources", "共享資源的矩陣組織"),
    ("a newly formed team after a merger", "併購後新組成的團隊"),
    ("a long-tenured team resistant to change", "抗拒變革的資深團隊"),
    ("a blended team of contractors and employees", "承攬商與員工混合團隊"),
]

COMPLICATIONS = [
    ("The sponsor expects results within six weeks.", "贊助者期望六週內見效。"),
    ("A recent audit flagged governance gaps.", "近期稽核指出治理缺口。"),
    ("Budget was cut fifteen percent mid-cycle.", "週期中期預算被削減百分之十五。"),
    ("Regulatory deadlines constrain your options.", "法規期限限制你的選項。"),
    ("Two executives publicly disagree on priorities.", "兩位高階主管公開對優先順序意見分歧。"),
    ("The previous PM left without documentation.", "前任 PM 未留文件即離職。"),
    ("Customer satisfaction scores are declining.", "客戶滿意度分數正在下降。"),
    ("A critical vendor contract expires next month.", "關鍵廠商合約下月到期。"),
    ("Union representatives have raised concerns.", "工會代表已提出疑慮。"),
    ("Media attention is increasing on this program.", "媒體對此計畫的關注度上升。"),
]

METHODOLOGY = [
    ("using a predictive stage-gate approach", "採預測式關卡方法"),
    ("following Scrum with two-week sprints", "遵循兩週衝刺 Scrum"),
    ("running a hybrid model with predictive infrastructure and agile delivery", "執行混合模式：基礎設施預測式、交付敏捷"),
    ("operating within a SAFe release train", "在 SAFe 發布火車中運作"),
    ("applying Kanban with WIP limits", "套用含 WIP 限制的 Kanban"),
    ("using iterative increments with quarterly milestones", "以季度里程碑進行迭代增量"),
]


def distribute(count: int, weights: list[int]) -> list[int]:
    total = sum(weights)
    raw = [count * w / total for w in weights]
    result = [int(x) for x in raw]
    rem = count - sum(result)
    fracs = [(raw[i] - result[i], i) for i in range(len(weights))]
    fracs.sort(reverse=True)
    for j in range(rem):
        result[fracs[j][1]] += 1
    return result


def assign_attributes(count: int, tasks: list[str]) -> list[tuple[str, str, int, bool]]:
    n_tasks = len(tasks)
    task_counts = distribute(count, [1] * n_tasks)
    approach_counts = distribute(count, APPROACH_WEIGHTS)
    diff_counts = distribute(count, DIFF_WEIGHTS)
    multi_count = round(count * 0.12)
    mcq_count = count - multi_count

    task_list: list[str] = []
    for i, c in enumerate(task_counts):
        task_list.extend([tasks[i]] * c)

    approaches: list[str] = []
    for i, c in enumerate(approach_counts):
        approaches.extend([APPROACHES[i]] * c)

    diffs: list[int] = []
    for i, c in enumerate(diff_counts):
        diffs.extend([DIFFICULTIES[i]] * c)

    types = [False] * mcq_count + [True] * multi_count
    import random
    rng = random.Random(42)
    combined = list(zip(task_list, approaches, diffs, types))
    rng.shuffle(combined)
    return combined


def combo_key(global_idx: int, task_idx: int) -> tuple:
    """Pick unique industry/team/complication/methodology combination."""
    n_ind = len(INDUSTRIES)
    n_team = len(TEAM_SIZES)
    n_comp = len(COMPLICATIONS)
    n_meth = len(METHODOLOGY)
    offset = task_idx * 1000 + global_idx
    ind = INDUSTRIES[offset % n_ind]
    team = TEAM_SIZES[(offset // n_ind) % n_team]
    comp = COMPLICATIONS[(offset // (n_ind * n_team)) % n_comp]
    meth = METHODOLOGY[(offset // (n_ind * n_team * n_comp)) % n_meth]
    variant = offset // (n_ind * n_team * n_comp * n_meth)
    return ind, team, comp, meth, variant


def opt(en: str, zh: str) -> dict:
    return {"en": en, "zh": zh}


def build_mcq(
    qid: str,
    domain: str,
    task: str,
    approach: str,
    difficulty: int,
    stem_en: str,
    stem_zh: str,
    correct_en: str,
    correct_zh: str,
    distractors: list[tuple[str, str]],
    tags: list[str],
    expl_builder: Callable | None = None,
) -> dict:
    options = [opt(correct_en, correct_zh)]
    for d_en, d_zh in distractors[:3]:
        options.append(opt(d_en, d_zh))
    correct = 0
    if expl_builder:
        exp_en, exp_zh = expl_builder(correct, [o["en"] for o in options], [o["zh"] for o in options])
    else:
        exp_en, exp_zh = default_explanation(correct, [o["en"] for o in options], [o["zh"] for o in options])
    return {
        "id": qid,
        "type": "mcq",
        "domain": domain,
        "task": task,
        "approach": approach,
        "difficulty": difficulty,
        "stem": {"en": stem_en, "zh": stem_zh},
        "options": options,
        "correct": correct,
        "explanation": {"en": exp_en, "zh": exp_zh},
        "tags": tags,
    }


def build_multi(
    qid: str,
    domain: str,
    task: str,
    approach: str,
    difficulty: int,
    stem_en: str,
    stem_zh: str,
    correct_pair: list[tuple[str, str]],
    wrong_opts: list[tuple[str, str]],
    tags: list[str],
) -> dict:
    options = [opt(*correct_pair[0]), opt(*correct_pair[1])]
    for w in wrong_opts[:3]:
        options.append(opt(*w))
    correct = [0, 1]
    exp_en, exp_zh = default_explanation(0, [o["en"] for o in options], [o["zh"] for o in options], is_multi=True, correct_indices=correct)
    return {
        "id": qid,
        "type": "multi",
        "domain": domain,
        "task": task,
        "approach": approach,
        "difficulty": difficulty,
        "stem": {"en": stem_en, "zh": stem_zh},
        "options": options,
        "correct": correct,
        "selectN": 2,
        "explanation": {"en": exp_en, "zh": exp_zh},
        "tags": tags,
    }


def default_explanation(
    correct_idx: int,
    options_en: list[str],
    options_zh: list[str],
    is_multi: bool = False,
    correct_indices: list[int] | None = None,
) -> tuple[str, str]:
    letters = "ABCDE"
    if is_multi and correct_indices:
        correct_set = set(correct_indices)
        parts_en, parts_zh = [], []
        for i in range(len(options_en)):
            label = letters[i]
            if i in correct_set:
                parts_en.append(
                    f"Option {label} is correct because it applies appropriate project management practices "
                    f"that directly address the scenario's constraints and stakeholder needs."
                )
                parts_zh.append(
                    f"選項 {label} 正確，因其套用符合情境限制與利害關係人需求的適當專案管理實務。"
                )
            else:
                parts_en.append(
                    f"Option {label} is incorrect because it either skips essential alignment, "
                    f"escalates prematurely, or fails to address the root cause described in the scenario."
                )
                parts_zh.append(
                    f"選項 {label} 錯誤，因其跳過必要對齊、過早升級或未處理情境所述根本原因。"
                )
        return " ".join(parts_en), " ".join(parts_zh)

    parts_en = [
        f"Option {letters[correct_idx]} is correct because it applies appropriate project management "
        f"practices that directly address the scenario's constraints and stakeholder needs."
    ]
    parts_zh = [
        f"選項 {letters[correct_idx]} 正確，因其套用符合情境限制與利害關係人需求的適當專案管理實務。"
    ]
    wrong_reasons_en = [
        "it skips essential alignment or facilitation and risks embedding wrong priorities",
        "it escalates prematurely or removes people before facilitation is attempted",
        "it defers critical work, allowing problems to persist and increase downstream impact",
    ]
    wrong_reasons_zh = [
        "其跳過必要對齊或引導，可能固化錯誤優先順序",
        "其過早升級或在未嘗試引導前就移除人員",
        "其延後關鍵工作，使問題持續並增加下游影響",
    ]
    wi = 0
    for i in range(len(options_en)):
        if i != correct_idx:
            parts_en.append(f"Option {letters[i]} is incorrect because {wrong_reasons_en[wi % 3]}.")
            parts_zh.append(f"選項 {letters[i]} 錯誤，因為{wrong_reasons_zh[wi % 3]}。")
            wi += 1
    return " ".join(parts_en), " ".join(parts_zh)


def write_json_file(filepath: Path, questions: list[dict]) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validate_unique_stems(questions: list[dict], label: str) -> None:
    stems = [q["stem"]["en"].strip().lower() for q in questions]
    if len(stems) != len(set(stems)):
        dupes = len(stems) - len(set(stems))
        raise ValueError(f"{label}: {dupes} duplicate stems found")
