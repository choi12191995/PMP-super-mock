#!/usr/bin/env python3
"""Generate unique Business domain scale-up questions BE-0016 through BE-0466."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scenario_engine import (
    OUTPUT_DIR,
    assign_attributes,
    build_mcq,
    build_multi,
    combo_key,
    validate_unique_stems,
    write_json_file,
)

FILES = [
    ("business-02.json", 16, 115),
    ("business-03.json", 116, 215),
    ("business-04.json", 216, 315),
    ("business-05.json", 316, 415),
    ("business-06.json", 416, 466),
]

TASKS = [f"BE{i}" for i in range(1, 9)]

TASK_CONTENT = {
    "BE1": {
        "situation": (
            "The enterprise PMO requires portfolio KPI reporting while the steering committee wants faster local dispute resolution without bypassing oversight.",
            "企業 PMO 要求組合 KPI 回報，指導委員會希望在供應商爭議上加快本地決策但不繞過監督。",
        ),
        "question": ("What should you implement first?", "你應首先實施什麼？"),
        "correct": (
            "Establish a delegated decision-rights matrix within the project governance framework clarifying local versus escalated authorities.",
            "在專案治理架構中建立委派決策權限矩陣，釐清本地與升級權限。",
        ),
        "distractors": [
            ("Send weekly status emails to the PMO without changing decision structures.", "向 PMO 發送每週狀態郵件而不改變決策結構。"),
            ("Remove the steering committee to reduce approval layers.", "移除指導委員會以減少核准層級。"),
            ("Create a risk register entry for disputes without defining decision pathways.", "僅在風險登記冊新增爭議項目，不定義決策路徑。"),
        ],
        "tags": ["governance", "PMO", "decision-rights"],
    },
    "BE2": {
        "situation": (
            "A new data privacy regulation affects how customer information is processed in the upcoming release.",
            "新資料隱私法規影響即將發布版本中客戶資訊的處理方式。",
        ),
        "question": ("What should you do first?", "你首先應做什麼？"),
        "correct": (
            "Engage legal and compliance, assess regulatory impact on requirements and architecture, and update the compliance register with mitigation actions.",
            "邀請法務與合規參與，評估法規對需求與架構的影響，並以緩解行動更新合規登記冊。",
        ),
        "distractors": [
            ("Proceed with release and address compliance findings post-launch.", "繼續發布，上線後再處理合規發現。"),
            ("Disable all data processing features until legal review completes next year.", "在明年法務審查完成前停用所有資料處理功能。"),
            ("Delegate compliance entirely to the vendor without internal review.", "將合規完全委派給廠商，不進行內部審查。"),
        ],
        "tags": ["compliance", "regulatory", "privacy"],
    },
    "BE3": {
        "situation": (
            "A senior executive requests a scope change that would alter the approved business case benefits.",
            "一位高階主管要求可能改變已核准業務案例效益的範圍變更。",
        ),
        "question": ("What is the appropriate response?", "適當回應為何？"),
        "correct": (
            "Route the request through integrated change control, analyze benefits and cost impacts, and present recommendations to the governance body.",
            "將請求導入整合變更控制，分析效益與成本影響，並向治理機構提出建議。",
        ),
        "distractors": [
            ("Implement the change immediately given the executive's authority.", "鑑於高階主管權威，立即實施變更。"),
            ("Reject the request verbally without impact documentation.", "口頭拒絕請求，不記錄影響。"),
            ("Add the work informally to avoid delaying the executive's initiative.", "非正式加入工作以避免延遲高階倡議。"),
        ],
        "tags": ["change-control", "business-case", "governance"],
    },
    "BE4": {
        "situation": (
            "Cross-functional teams report recurring impediments that block value delivery but no single owner resolves them.",
            "跨職能團隊回報阻礙價值交付的 recurring 障礙，但無單一負責人解決。",
        ),
        "question": ("What should you do?", "你應做什麼？"),
        "correct": (
            "Maintain an impediment log with owners and SLAs, facilitate resolution sessions with accountable leaders, and track removal in status reviews.",
            "維護含負責人與 SLA 的障礙日誌，與問責領導人引導解決會議，並在狀態審查中追蹤移除。",
        ),
        "distractors": [
            ("Ask teams to work around impediments without escalation.", "要求團隊繞過障礙而不升級。"),
            ("Log impediments but defer action until phase end.", "記錄障礙但延後行動至階段結束。"),
            ("Transfer all impediments to the PMO without context.", "在無背景說明下將所有障礙轉交 PMO。"),
        ],
        "tags": ["impediments", "issue-management", "escalation"],
    },
    "BE5": {
        "situation": (
            "A newly identified supply chain risk could delay critical path activities if materialized.",
            "新識別的供應鏈風險若成真可能延遲關鍵路徑活動。",
        ),
        "question": ("What should you do next?", "你接下來應做什麼？"),
        "correct": (
            "Update the risk register with qualitative and quantitative analysis, define response strategies, assign owners, and monitor triggers.",
            "以定性與定量分析更新風險登記冊，定義回應策略，指派負責人並監控觸發條件。",
        ),
        "distractors": [
            ("Accept the risk without documentation to avoid alarming stakeholders.", "不記錄即接受風險以避免驚動利害關係人。"),
            ("Transfer all supply risk to the vendor contract without analysis.", "未分析即將所有供應風險轉移至廠商合約。"),
            ("Delay risk response until the risk actually occurs.", "延後風險回應直至風險實際發生。"),
        ],
        "tags": ["risk-management", "supply-chain", "response-planning"],
    },
    "BE6": {
        "situation": (
            "Retrospectives repeatedly surface the same process inefficiencies but improvement actions stall after each cycle.",
            "回顧反覆浮現相同流程低效，但每週期後改善行動停滯。",
        ),
        "question": ("What should you do to drive continuous improvement?", "為推動持續改善，你應做什麼？"),
        "correct": (
            "Prioritize improvement items with measurable outcomes, assign accountable owners, integrate actions into the backlog, and review progress in governance forums.",
            "以可衡量成果排序改善項目，指派問責負責人，將行動整合至待辦清單，並在治理論壇審查進度。",
        ),
        "distractors": [
            ("Stop retrospectives until delivery pressure eases.", "在交付壓力緩解前停止回顧。"),
            ("Document lessons but take no committed actions.", "記錄經驗教訓但不採取承諾行動。"),
            ("Outsource improvement to consultants without team involvement.", "在無團隊參與下將改善外包給顧問。"),
        ],
        "tags": ["continuous-improvement", "retrospective", "Kaizen"],
    },
    "BE7": {
        "situation": (
            "The solution requires significant changes to frontline workflows but change readiness scores are low in affected departments.",
            "解決方案需大幅改變第一線工作流程，但受影響部門變革準備度分數偏低。",
        ),
        "question": ("What should you do first?", "你首先應做什麼？"),
        "correct": (
            "Develop a change management plan with stakeholder analysis, training, communications, and reinforcement aligned to adoption milestones.",
            "制定含利害關係人分析、訓練、溝通與強化措施的變革管理計畫，對齊採用里程碑。",
        ),
        "distractors": [
            ("Deploy the solution and address resistance during hypercare only.", "部署解決方案，僅在超級維護期處理抗拒。"),
            ("Mandate adoption by policy without engagement activities.", "以政策強制採用，不進行參與活動。"),
            ("Limit communications to IT staff since they implement the tool.", "溝通僅限 IT 人員，因其實施工具。"),
        ],
        "tags": ["organizational-change", "adoption", "change-management"],
    },
    "BE8": {
        "situation": (
            "Market shifts and competitor moves may invalidate assumptions in the business case within the next quarter.",
            "市場轉變與競爭對手動作可能在下一季使業務案例假設失效。",
        ),
        "question": ("What should you do?", "你應做什麼？"),
        "correct": (
            "Monitor external environment factors, reassess business case assumptions with finance and strategy, and recommend continue, pivot, or pause decisions to governance.",
            "監控外部環境因素，與財務及策略重評業務案例假設，並向治理機構建議繼續、轉向或暫停決策。",
        ),
        "distractors": [
            ("Ignore market signals until the original business case expires.", "忽略市場訊號直至原業務案例到期。"),
            ("Cancel the project immediately without structured assessment.", "未經結構化評估即立即取消專案。"),
            ("Continue execution without informing sponsors of environmental changes.", "在未告知贊助者環境變化下繼續執行。"),
        ],
        "tags": ["external-environment", "business-case", "strategic-alignment"],
    },
}

MULTI_SUFFIX = (" Select the TWO best actions.", " 選擇兩項最佳行動。")

MULTI_SECOND = {
    "BE1": (
        "Document governance roles and escalation thresholds in the project charter.",
        "在專案章程中記錄治理角色與升級門檻。",
    ),
    "BE2": (
        "Schedule compliance validation before release gate approval.",
        "在發布關卡核准前安排合規驗證。",
    ),
    "BE3": (
        "Update the benefits register if the change is approved.",
        "若變更獲核准，更新效益登記冊。",
    ),
    "BE4": (
        "Review impediment trends in the next governance meeting.",
        "於下次治理會議審查障礙趨勢。",
    ),
    "BE5": (
        "Align risk responses with contingency reserve usage rules.",
        "使風險回應與應急儲備使用規則對齊。",
    ),
    "BE6": (
        "Celebrate implemented improvements to reinforce the culture.",
        "慶祝已實施改善以強化文化。",
    ),
    "BE7": (
        "Identify change champions in each affected department.",
        "在各受影響部門識別變革倡導者。",
    ),
    "BE8": (
        "Establish environmental scanning triggers in the risk register.",
        "在風險登記冊建立環境掃描觸發條件。",
    ),
}

MULTI_WRONG = [
    ("Defer all business analysis until project closure.", "延後所有業務分析至專案結案。"),
    ("Make unilateral decisions without governance review.", "未經治理審查即單方面決策。"),
    ("Ignore stakeholder input on business impacts.", "忽略利害關係人對業務影響的意見。"),
]


def build_stem(task: str, global_idx: int, task_idx: int) -> tuple[str, str]:
    ind, team, comp, meth, var = combo_key(global_idx, task_idx)
    content = TASK_CONTENT[task]
    var_notes_en = [
        " The board review is in ten days.",
        " Internal audit flagged related control gaps.",
        " A strategic partner merger was announced yesterday.",
        " Customer churn increased after the last release.",
    ]
    var_notes_zh = [
        " 董事會審查在十天後。",
        " 內部稽核指出相關控制缺口。",
        " 策略夥伴合併昨日宣布。",
        " 上次發布後客戶流失增加。",
    ]
    stem_en = (
        f"You are leading a {ind[2]} program {meth[0]}. "
        f"You coordinate {team[0]}. {content['situation'][0]} {comp[0]}{var_notes_en[var % 4]} "
        f"{content['question'][0]}"
    )
    stem_zh = (
        f"你領導{ind[3]}計畫，{meth[1]}。"
        f"你協調{team[1]}。{content['situation'][1]}{comp[1]}{var_notes_zh[var % 4]}"
        f"{content['question'][1]}"
    )
    return stem_en, stem_zh


def generate_question(qid: str, task: str, approach: str, difficulty: int, is_multi: bool, global_idx: int, task_idx: int) -> dict:
    content = TASK_CONTENT[task]
    stem_en, stem_zh = build_stem(task, global_idx, task_idx)

    if is_multi:
        stem_en += MULTI_SUFFIX[0]
        stem_zh += MULTI_SUFFIX[1]
        return build_multi(
            qid, "business", task, approach, difficulty,
            stem_en, stem_zh,
            [content["correct"], MULTI_SECOND[task]],
            MULTI_WRONG + content["distractors"][:1],
            content["tags"],
        )

    return build_mcq(
        qid, "business", task, approach, difficulty,
        stem_en, stem_zh,
        content["correct"][0], content["correct"][1],
        content["distractors"],
        content["tags"],
    )


def generate_file(filename: str, start_num: int, end_num: int) -> list[dict]:
    count = end_num - start_num + 1
    attrs = assign_attributes(count, TASKS)
    task_counters = {t: 0 for t in TASKS}
    questions = []

    for i, num in enumerate(range(start_num, end_num + 1)):
        qid = f"BE-{num:04d}"
        task, approach, difficulty, is_multi = attrs[i]
        tidx = task_counters[task]
        task_counters[task] += 1
        questions.append(generate_question(qid, task, approach, difficulty, is_multi, num, tidx))

    write_json_file(OUTPUT_DIR / filename, questions)
    validate_unique_stems(questions, filename)
    return questions


def main() -> None:
    total = 0
    for filename, start, end in FILES:
        qs = generate_file(filename, start, end)
        print(f"Wrote {len(qs)} questions to {filename}")
        total += len(qs)
    print(f"Total business scale-up: {total}")


if __name__ == "__main__":
    main()
