#!/usr/bin/env python3
"""Generate unique Process domain scale-up questions PRC-0026 through PRC-0734."""

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
    ("process-02.json", 26, 125),
    ("process-03.json", 126, 225),
    ("process-04.json", 226, 325),
    ("process-05.json", 326, 425),
    ("process-06.json", 426, 525),
    ("process-07.json", 526, 625),
    ("process-08.json", 626, 734),
]

TASKS = [f"PRC{i}" for i in range(1, 11)]

TASK_CONTENT = {
    "PRC1": {
        "situation": (
            "Functional managers want to start execution before subsidiary plans are consolidated into an integrated baseline.",
            "職能經理希望在子計畫整合成整合基準前即開始執行。",
        ),
        "question": ("What should you do first?", "你首先應做什麼？"),
        "correct": (
            "Integrate subsidiary plans into the project management plan and obtain formal approval before authorizing execution.",
            "將各子計畫整合成專案管理計畫，並在授權執行前取得正式核准。",
        ),
        "distractors": [
            ("Authorize long-lead procurement in parallel with plan finalization.", "在計畫定稿同時授權長交期採購。"),
            ("Submit only the schedule plan for approval since it drives all work.", "僅提交時程計畫核准，因其驅動所有工作。"),
            ("Begin baseline work using the most complete subsidiary plan available.", "依現有最完整子計畫開始基準化工作。"),
        ],
        "tags": ["integrated-management", "project-management-plan", "baseline"],
    },
    "PRC2": {
        "situation": (
            "Stakeholders request features not in the approved scope baseline while the team is mid-sprint.",
            "利害關係人在團隊衝刺中期要求未納入已核准範圍基準的功能。",
        ),
        "question": ("What is the best approach?", "最佳做法是什麼？"),
        "correct": (
            "Evaluate the request through the change control process, assess impact on scope baseline and schedule, and present options to the change board.",
            "透過變更控制流程評估請求，分析對範圍基準與時程的影響，並向變更委員會提出選項。",
        ),
        "distractors": [
            ("Accept the work immediately to maintain stakeholder satisfaction.", "立即接受工作以維持利害關係人滿意度。"),
            ("Reject all requests verbally without documenting rationale.", "口頭拒絕所有請求，不記錄理由。"),
            ("Add features directly to the sprint backlog without impact analysis.", "未做影響分析即直接加入衝刺待辦清單。"),
        ],
        "tags": ["scope-management", "change-control", "baseline"],
    },
    "PRC3": {
        "situation": (
            "Leadership asks how business value will be demonstrated before teams finish building complete specifications.",
            "領導詢問在團隊完成全部規格前如何展現業務價值。",
        ),
        "question": ("What should you recommend?", "你應建議什麼？"),
        "correct": (
            "Define a minimum viable product slice with measurable outcomes, prioritize by value, and plan iterative releases with feedback loops.",
            "定義具可衡量成果的最小可行產品切片，依價值排序，並規劃含回饋循環的迭代發布。",
        ),
        "distractors": [
            ("Deliver the full specification in a single release.", "單次發布交付完整規格。"),
            ("Ignore business value and optimize for technical completeness.", "忽略業務價值，優化技術完整度。"),
            ("Stop measuring outcomes after initial launch.", "初次上線後停止衡量成果。"),
        ],
        "tags": ["value-delivery", "mvp", "benefits-realization"],
    },
    "PRC4": {
        "situation": (
            "Critical specialists are overallocated across three concurrent workstreams and quality is slipping.",
            "關鍵專家同時過度分配於三個並行工作流，品質正在下滑。",
        ),
        "question": ("What should you do first?", "你首先應做什麼？"),
        "correct": (
            "Analyze resource utilization, negotiate priorities with functional managers, and update the resource management plan with realistic allocations.",
            "分析資源利用率，與職能經理協商優先順序，並以現實分配更新資源管理計畫。",
        ),
        "distractors": [
            ("Hire contractors without assessing skill fit or onboarding time.", "未評估技能契合或 onboarding 時間即聘承攬商。"),
            ("Extend working hours indefinitely without changing assignments.", "無限期延長工時而不改變分派。"),
            ("Remove quality activities to free specialist time.", "移除品質活動以釋出專家時間。"),
        ],
        "tags": ["resource-management", "allocation", "capacity"],
    },
    "PRC5": {
        "situation": (
            "A preferred vendor's proposal exceeds budget but offers proprietary technology the team favors.",
            "偏好廠商提案超出預算，但提供團隊偏好的專有技術。",
        ),
        "question": ("What should you do before awarding the contract?", "在授予合約前你應做什麼？"),
        "correct": (
            "Conduct a structured procurement review comparing cost, risk, and compliance against selection criteria documented in the procurement management plan.",
            "依採購管理計畫所載選擇準則，進行比較成本、風險與合規的結構化採購審查。",
        ),
        "distractors": [
            ("Award immediately to avoid schedule delay.", "立即授予以避免時程延誤。"),
            ("Negotiate only price without revisiting technical requirements.", "僅議價而不重新審視技術需求。"),
            ("Split the contract informally across multiple POs to bypass approval limits.", "以多張 PO 非正式拆分合約以繞過核准限額。"),
        ],
        "tags": ["procurement", "vendor-selection", "compliance"],
    },
    "PRC6": {
        "situation": (
            "Earned value metrics show cost performance index below 0.85 while leadership expects no scope reduction.",
            "挣值指標顯示成本績效指數低於 0.85，而領導期望不縮減範圍。",
        ),
        "question": ("What should you recommend?", "你應建議什麼？"),
        "correct": (
            "Perform integrated cost-schedule analysis, forecast EAC using appropriate methods, and present recovery options with trade-offs to governance.",
            "執行整合成本時程分析，以適當方法預測 EAC，並向治理機構提出含權衡的追回選項。",
        ),
        "distractors": [
            ("Rebaseline immediately without root-cause analysis.", "未做根本原因分析即立即重訂基準。"),
            ("Report optimistic ETC assuming future efficiency gains without evidence.", "在無證據下假設未來效率提升而回報樂觀 ETC。"),
            ("Defer financial reporting until the next fiscal quarter.", "延後財務報告至下一會計季。"),
        ],
        "tags": ["EVM", "cost-management", "forecasting"],
    },
    "PRC7": {
        "situation": (
            "Quality metrics show increasing defect rates and the team debates adding a final inspection phase only.",
            "品質指標顯示缺陷率上升，團隊僅爭論是否增加最終檢驗階段。",
        ),
        "question": ("What should you do?", "你應怎麼做？"),
        "correct": (
            "Investigate special-cause variation, implement corrective actions per the quality management plan, and integrate prevention practices into the process.",
            "調查特殊原因變異，依品質管理計畫實施矯正行動，並將預防實務整合至流程。",
        ),
        "distractors": [
            ("Add inspection headcount without changing the process.", "不改流程，僅增加檢驗人力。"),
            ("Accept higher defect rates to protect the schedule.", "為保時程接受較高缺陷率。"),
            ("Blame the vendor without root-cause analysis.", "未做根本原因分析即归咎廠商。"),
        ],
        "tags": ["quality-management", "process-improvement", "prevention"],
    },
    "PRC8": {
        "situation": (
            "A committed milestone is at risk and the schedule model shows limited float on the critical path.",
            "承諾里程碑有風險，時程模型顯示關鍵路徑浮時有限。",
        ),
        "question": ("After updating the schedule model, what should you apply first?", "更新時程模型後，你應優先採用什麼？"),
        "correct": (
            "Analyze critical path activities, evaluate compression options with risk review, and recommend fast-tracking or crashing where dependencies allow.",
            "分析關鍵路徑活動，在風險審查下評估壓縮選項，並在相依性允許處建議快速追蹤或趕工。",
        ),
        "distractors": [
            ("Remove compliance activities from the schedule without change control.", "未經變更控制自時程移除合規活動。"),
            ("Delete buffer tasks to show an earlier finish date.", "刪除緩衝任務以顯示較早完工日。"),
            ("Report an earlier date without changing activity logic.", "不改變活動邏輯即報告較早日期。"),
        ],
        "tags": ["schedule-management", "critical-path", "compression"],
    },
    "PRC9": {
        "situation": (
            "Status reports from workstreams show conflicting percent complete values for the same deliverables.",
            "各工作流狀態報告對相同可交付成果顯示矛盾的完成百分比。",
        ),
        "question": ("What should you do to evaluate project status accurately?", "為準確評估專案狀態，你應做什麼？"),
        "correct": (
            "Reconcile progress against the WBS and acceptance criteria, validate data with workstream leads, and update integrated status using agreed measurement rules.",
            "依 WBS 與驗收準則核對進度，與工作流負責人驗證資料，並以共識衡量規則更新整合狀態。",
        ),
        "distractors": [
            ("Average the conflicting percentages for the executive dashboard.", "為高階儀表板平均衝突百分比。"),
            ("Accept the most optimistic report to maintain stakeholder confidence.", "採納最樂觀報告以維持利害關係人信心。"),
            ("Stop reporting percent complete and use only milestone colors.", "停止報告完成百分比，僅用里程碑顏色。"),
        ],
        "tags": ["status-reporting", "progress-measurement", "WBS"],
    },
    "PRC10": {
        "situation": (
            "The final deliverable is accepted but operations, finance, and the PMO each require different closure artifacts.",
            "最終可交付成果已驗收，但維運、財務與 PMO 各自要求不同結案文件。",
        ),
        "question": ("What should you do to close the project effectively?", "為有效結案，你應做什麼？"),
        "correct": (
            "Execute the closure checklist in the project management plan, obtain formal acceptance, archive records, and capture lessons learned with stakeholders.",
            "執行專案管理計畫中的結案檢核表，取得正式驗收，歸檔紀錄，並與利害關係人擷取經驗教訓。",
        ),
        "distractors": [
            ("Release the team immediately without administrative closure.", "立即釋出團隊，不進行行政結案。"),
            ("Skip lessons learned to accelerate transition to operations.", "跳過經驗教訓以加速移交維運。"),
            ("Close only the technical workstream and leave contracts open.", "僅結案技術工作流，合約保持開放。"),
        ],
        "tags": ["project-closure", "lessons-learned", "transition"],
    },
}

MULTI_SUFFIX = (" Select the TWO best actions.", " 選擇兩項最佳行動。")

MULTI_SECOND = {
    "PRC1": (
        "Document tailoring decisions and how predictive and adaptive elements integrate in the plan.",
        "記錄裁剪決策及預測式與適應性元素在計畫中的整合方式。",
    ),
    "PRC2": (
        "Update the requirements traceability matrix if the change is approved.",
        "若變更獲核准，更新需求追溯矩陣。",
    ),
    "PRC3": (
        "Establish feedback metrics tied to each release increment.",
        "建立與各發布增量連結的回饋指標。",
    ),
    "PRC4": (
        "Escalate persistent overallocation through the resource management plan.",
        "依資源管理計畫升級持續過度分配問題。",
    ),
    "PRC5": (
        "Verify vendor compliance with security and legal requirements before award.",
        "授予前驗證廠商符合資安與法務要求。",
    ),
    "PRC6": (
        "Review contingency and management reserve usage with the controller.",
        "與財務控制人員審查應急與管理儲備使用。",
    ),
    "PRC7": (
        "Facilitate a retrospective to identify systemic quality improvements.",
        "引導回顧以識別系統性品質改善。",
    ),
    "PRC8": (
        "Communicate recovery plan impacts to affected stakeholders.",
        "向受影響利害關係人溝通追回計畫影響。",
    ),
    "PRC9": (
        "Trend variance data to detect early performance drift.",
        "趨勢分析差異資料以偵測早期績效偏移。",
    ),
    "PRC10": (
        "Confirm contract closure and final financial reconciliation.",
        "確認合約結案與最終財務核對。",
    ),
}

MULTI_WRONG = [
    ("Bypass governance to accelerate delivery.", "繞過治理以加速交付。"),
    ("Defer documentation until after team release.", "延後文件化至團隊釋出後。"),
    ("Ignore baseline impacts when making decisions.", "做決策時忽略基準影響。"),
]


def build_stem(task: str, global_idx: int, task_idx: int) -> tuple[str, str]:
    ind, team, comp, meth, var = combo_key(global_idx, task_idx)
    content = TASK_CONTENT[task]
    var_notes_en = [
        " Integration testing starts next week.",
        " A regulatory inspection is scheduled mid-cycle.",
        " The PMO requires traceability for audit.",
        " Vendor performance has been inconsistent.",
    ]
    var_notes_zh = [
        " 整合測試下週開始。",
        " 週期中期排定法規檢查。",
        " PMO 要求可追溯性以供稽核。",
        " 廠商績效一直不穩定。",
    ]
    stem_en = (
        f"You are managing a {ind[2]} initiative {meth[0]}. "
        f"You work with {team[0]}. {content['situation'][0]} {comp[0]}{var_notes_en[var % 4]} "
        f"{content['question'][0]}"
    )
    stem_zh = (
        f"你管理{ind[3]}計畫，{meth[1]}。"
        f"你與{team[1]}協作。{content['situation'][1]}{comp[1]}{var_notes_zh[var % 4]}"
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
            qid, "process", task, approach, difficulty,
            stem_en, stem_zh,
            [content["correct"], MULTI_SECOND[task]],
            MULTI_WRONG + content["distractors"][:1],
            content["tags"],
        )

    return build_mcq(
        qid, "process", task, approach, difficulty,
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
        qid = f"PRC-{num:04d}"
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
    print(f"Total process scale-up: {total}")


if __name__ == "__main__":
    main()
