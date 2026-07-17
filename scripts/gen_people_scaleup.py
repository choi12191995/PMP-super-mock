#!/usr/bin/env python3
"""Generate unique People domain scale-up questions PPL-0021 through PPL-0592."""

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
    ("people-02.json", 21, 120),
    ("people-03.json", 121, 220),
    ("people-04.json", 221, 320),
    ("people-05.json", 321, 420),
    ("people-06.json", 421, 520),
    ("people-07.json", 521, 592),
]

TASKS = [f"PPL{i}" for i in range(1, 9)]

# Task-specific action templates indexed by variant
TASK_CONTENT = {
    "PPL1": {
        "situation": (
            "Stakeholders from multiple departments interpret program success differently and weekly priorities conflict.",
            "多部門利害關係人對計畫成功定義不同，每週優先順序相互衝突。",
        ),
        "question": ("What should you do FIRST to develop a common vision?", "為建立共同願景，您首先應做什麼？"),
        "correct": (
            "Facilitate a structured vision workshop where stakeholders co-create objectives, success measures, and guiding principles documented in a team charter.",
            "主持結構化願景工作坊，引導利害關係人共同制定目標、成功衡量與指導原則，並記錄於團隊章程。",
        ),
        "distractors": [
            ("Publish a detailed WBS so teams stop debating goals and start executing.", "發布詳細 WBS，讓團隊停止辯論目標並開始執行。"),
            ("Ask the sponsor to mandate one department's priorities over all others.", "請發起人下令某一部門優先順序凌駕所有其他部門。"),
            ("Defer vision alignment until all requirements are legally approved.", "延後願景對齊，直至所有需求獲法務核准。"),
        ],
        "tags": ["common-vision", "team-charter", "facilitation"],
    },
    "PPL2": {
        "situation": (
            "Two senior team members argue loudly during planning about technical approach while others stop participating.",
            "兩位資深成員在規劃中激烈爭論技術做法，其他成員已停止參與。",
        ),
        "question": ("What is the most appropriate response?", "最適當的回應為何？"),
        "correct": (
            "Facilitate a focused discussion using agreed team norms, help both sides state interests, and guide the team toward a workable solution.",
            "依團隊共識規範引導聚焦討論，協助雙方表達利益訴求，並引導團隊朝向可行解決方案前進。",
        ),
        "distractors": [
            ("Split the members into separate sub-teams to avoid further conflict.", "將成員分至不同子團隊以避免再度衝突。"),
            ("Escalate immediately to management and ask them to remove one member.", "立即升級至管理階層，請其移除其中一位成員。"),
            ("Postpone planning until both members submit written position papers.", "延後規劃，待雙方提交書面立場說明。"),
        ],
        "tags": ["conflict-resolution", "team-norms", "facilitation"],
    },
    "PPL3": {
        "situation": (
            "The team consistently misses commitments and morale is low after a failed release. The sponsor asks how you will restore effective leadership.",
            "團隊持續未達承諾，發布失敗後士氣低落。贊助者詢問您如何恢復有效領導。",
        ),
        "question": ("What should you do FIRST?", "您首先應做什麼？"),
        "correct": (
            "Meet individually and with the team to understand blockers, clarify priorities, remove impediments, and re-establish achievable goals with visible support.",
            "個別及團隊會談以了解阻礙、釐清優先順序、移除障礙，並在可見支持下重新建立可達成目標。",
        ),
        "distractors": [
            ("Replace half the team immediately to send a performance message.", "立即替換半数團隊以傳達績效訊息。"),
            ("Increase overtime requirements without discussing root causes.", "在未討論根本原因下提高加班要求。"),
            ("Report green status to the sponsor to avoid further scrutiny.", "向贊助者回報綠燈狀態以避免進一步審查。"),
        ],
        "tags": ["team-leadership", "impediments", "motivation"],
    },
    "PPL4": {
        "situation": (
            "Key stakeholders were engaged late and request mid-cycle changes. Delivery cadence is stable but engagement scores are low.",
            "關鍵利害關係人較晚參與並要求週期中期變更。交付節奏穩定但參與度分數偏低。",
        ),
        "question": ("What improves stakeholder engagement without destabilizing delivery?", "如何在動搖交付的前提下提升利害關係人參與？"),
        "correct": (
            "Invite key stakeholders to structured review and refinement sessions, capture requests in the backlog, and clarify how feedback enters future cycles.",
            "邀請關鍵利害關係人參加結構化審查與精煉會議，將需求納入待辦清單，並說明回饋如何進入後續週期。",
        ),
        "distractors": [
            ("Exclude late stakeholders until they complete formal training.", "排除晚加入者直至完成正式訓練。"),
            ("Accept all change requests immediately and replan the current cycle.", "立即接受所有變更要求並重規劃當前週期。"),
            ("Send weekly email summaries and avoid live collaboration sessions.", "僅發送每週電郵摘要，避免現場協作會議。"),
        ],
        "tags": ["stakeholder-engagement", "backlog-refinement", "collaboration"],
    },
    "PPL5": {
        "situation": (
            "Business and technical stakeholders hold different assumptions about scope boundaries and acceptance criteria for the next phase.",
            "業務與技術利害關係人對下一階段範圍邊界與驗收準則持有不同假設。",
        ),
        "question": ("What should you do to align expectations?", "您應如何對齊期望？"),
        "correct": (
            "Facilitate an expectations workshop to document shared assumptions, acceptance criteria, and decision rules in an updated stakeholder engagement plan.",
            "引導期望工作坊，記錄共同假設、驗收準則與決策規則於更新的利害關係人參與計畫。",
        ),
        "distractors": [
            ("Proceed with technical assumptions and inform business stakeholders later.", "依技術假設推進，稍後再通知業務利害關係人。"),
            ("Ask the sponsor to pick one group's expectations without discussion.", "請發起人未經討論即選定一方期望。"),
            ("Delay alignment until user acceptance testing begins.", "延後對齊至使用者驗收測試開始。"),
        ],
        "tags": ["expectations", "stakeholder-alignment", "acceptance-criteria"],
    },
    "PPL6": {
        "situation": (
            "A vocal stakeholder continues requesting scope additions that were previously deferred, creating tension in steering meetings.",
            "某位強勢利害關係人持續要求先前已延後的範圍增加，在指導會議中造成緊張。",
        ),
        "question": ("What is the BEST approach to manage this stakeholder's expectations?", "管理此利害關係人期望的最佳做法為何？"),
        "correct": (
            "Meet privately to review the change control process, confirm priorities against the baseline, and agree on a transparent path for future requests.",
            "私下會談審查變更控制流程，依基準確認優先順序，並就未來請求達成透明路徑共識。",
        ),
        "distractors": [
            ("Approve all requests to preserve the relationship regardless of impact.", "不論影響如何均核准所有請求以維繫關係。"),
            ("Remove the stakeholder from the register to reduce meeting conflict.", "從登記冊移除該利害關係人以減少會議衝突。"),
            ("Publicly decline all future requests without further dialogue.", "公開拒絕所有未來請求，不再進一步對話。"),
        ],
        "tags": ["stakeholder-management", "change-control", "expectations"],
    },
    "PPL7": {
        "situation": (
            "Several specialists who built critical components will leave before handover. Operations staff express concern about sustaining the solution.",
            "數位建構關鍵元件的專家將在交接前離職。維運人員對永續維護解決方案表示擔憂。",
        ),
        "question": ("What should you do to ensure effective knowledge transfer?", "您應如何確保有效知識移轉？"),
        "correct": (
            "Plan structured knowledge-transfer sessions, pair departing specialists with operations staff, and document runbooks before transition.",
            "規劃結構化知識移轉會議，配對即將離職專家與維運人員，並在轉換前文件化運維手冊。",
        ),
        "distractors": [
            ("Rely on existing documentation without live transfer sessions.", "僅依賴現有文件，不舉辦現場移轉會議。"),
            ("Delay knowledge transfer until after go-live when issues arise.", "延後知識移轉至上線後問題出現時。"),
            ("Outsource all sustainment to a vendor without internal training.", "將所有維護外包給廠商，不進行內部訓練。"),
        ],
        "tags": ["knowledge-transfer", "transition", "operations"],
    },
    "PPL8": {
        "situation": (
            "Remote teams, executives, and external partners receive inconsistent messages about milestone status and upcoming decisions.",
            "遠端團隊、高階主管與外部夥伴收到關於里程碑狀態與即將決策的不一致訊息。",
        ),
        "question": ("What should you do FIRST to improve communication?", "為改善溝通，您首先應做什麼？"),
        "correct": (
            "Review and update the communications management plan with agreed channels, frequency, owners, and escalation paths for each audience.",
            "審查並更新溝通管理計畫，為各受众訂定管道、頻率、負責人與升級路徑。",
        ),
        "distractors": [
            ("Send daily all-hands emails with every detail to all recipients.", "向所有收件人每日發送含所有細節的全員電郵。"),
            ("Limit updates to the sponsor only until confusion resolves itself.", "僅向贊助者提供更新，直至混淆自行解決。"),
            ("Allow each workstream lead to define their own messaging without coordination.", "允許各工作流負責人無需協調即自行定義訊息。"),
        ],
        "tags": ["communications", "stakeholder-updates", "planning"],
    },
}

MULTI_SUFFIX = (
    " Select the TWO best actions.",
    " 選擇兩項最佳行動。",
)

MULTI_SECOND = {
    "PPL1": (
        "Document agreed success measures and guiding principles in a team charter accessible to all workstreams.",
        "將共識成功衡量與指導原則記錄於各工作流可存取的團隊章程。",
    ),
    "PPL2": (
        "Confirm team working agreements and revisit them if conflict patterns repeat.",
        "確認團隊工作協議，若衝突模式重複則重新審視。",
    ),
    "PPL3": (
        "Coach team leads on removing impediments and celebrating incremental wins.",
        "指導團隊負責人移除障礙並慶祝漸進成果。",
    ),
    "PPL4": (
        "Update the stakeholder register with engagement strategies per influence level.",
        "依影響力層級更新利害關係人登記冊的參與策略。",
    ),
    "PPL5": (
        "Publish a decision log capturing agreed assumptions and open questions.",
        "發布決策紀錄，記錄已同意假設與待釐清問題。",
    ),
    "PPL6": (
        "Facilitate a prioritization session referencing the approved scope baseline.",
        "引導優先順序會議，參照已核准範圍基準。",
    ),
    "PPL7": (
        "Schedule shadowing sessions before specialists depart.",
        "在專家離職前安排跟岗學習會議。",
    ),
    "PPL8": (
        "Establish a single source of truth for status reporting across channels.",
        "建立跨管道狀態報告的單一可信來源。",
    ),
}

MULTI_WRONG = [
    ("Escalate all issues to the sponsor without team discussion.", "未經團隊討論即將所有問題升級至贊助者。"),
    ("Skip documentation and rely on informal hallway conversations.", "跳過文件化，依賴非正式走廊對話。"),
    ("Delay action until the next phase gate regardless of urgency.", "不論緊急程度均延後行動至下一階段關卡。"),
]


def build_stem(task: str, global_idx: int, task_idx: int) -> tuple[str, str]:
    ind, team, comp, meth, var = combo_key(global_idx, task_idx)
    content = TASK_CONTENT[task]
    var_note_en = [
        " Delivery has already started without alignment.",
        " A recent reorganization changed reporting lines.",
        " The contract includes strict milestone penalties.",
        " Customer feedback highlights confusion about goals.",
    ][var % 4]
    var_note_zh = [
        " 交付已在未對齊情況下啟動。",
        " 近期重組已改變報告線。",
        " 合約包含嚴格里程碑罰則。",
        " 客戶回饋強調對目標的混淆。",
    ][var % 4]

    stem_en = (
        f"You are the project manager for a {ind[2]} program {meth[0]}. "
        f"You lead {team[0]}. {content['situation'][0]} {comp[0]}{var_note_en} "
        f"{content['question'][0]}"
    )
    stem_zh = (
        f"您是{ind[3]}計畫的專案經理，{meth[1]}。"
        f"您帶領{team[1]}。{content['situation'][1]}{comp[1]}{var_note_zh}"
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
            qid, "people", task, approach, difficulty,
            stem_en, stem_zh,
            [content["correct"], MULTI_SECOND[task]],
            MULTI_WRONG + content["distractors"][:1],
            content["tags"],
        )

    return build_mcq(
        qid, "people", task, approach, difficulty,
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
        qid = f"PPL-{num:04d}"
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
    print(f"Total people scale-up: {total}")


if __name__ == "__main__":
    main()
