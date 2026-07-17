#!/usr/bin/env python3
"""Generate PMP Process domain questions PRC-0026 through PRC-0634."""

import json
import random
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "public" / "questions"
random.seed(20260718)

FILES = [
    ("process-02.json", 26, 125),
    ("process-03.json", 126, 225),
    ("process-04.json", 226, 325),
    ("process-05.json", 326, 425),
    ("process-06.json", 426, 525),
    ("process-07.json", 526, 625),   # 100 questions (PRC-0526–0625)
    ("process-08.json", 626, 734),   # 109 questions: PRC-0626–0734 (incl. user tail + fill to 709)
]

TASKS = [f"PRC{i}" for i in range(1, 11)]
APPROACHES = ["predictive", "agile", "hybrid"]
APPROACH_WEIGHTS = [40, 30, 30]
DIFFICULTIES = [1, 2, 3]
DIFF_WEIGHTS = [25, 50, 25]


def S(stem_en, stem_zh, correct_en, correct_zh, d1, d2, d3, d4, tags):
    return (stem_en, stem_zh, correct_en, correct_zh, [d1, d2, d3, d4], tags)


def expand(task, items):
    """Repeat template tuples with variant suffixes for larger banks."""
    out = []
    for i, item in enumerate(items):
        if len(item) == 9:
            stem_en, stem_zh, c_en, c_zh, d1, d2, d3, d4, tags = item
            out.append(S(stem_en, stem_zh, c_en, c_zh, d1, d2, d3, d4, tags))
        else:
            out.append(item)
    return out


# --- Scenario banks per PRC task ---

PRC1_BASE = [
    S(
        "You are managing a hospital expansion using a predictive approach. Functional managers want to start procurement before the integrated plan is approved. Subsidiary plans for scope, schedule, and cost are drafted but not consolidated. What should you do first?",
        "你正以預測式方法管理醫院擴建專案。職能經理希望在整合計畫核准前啟動採購。範疇、時程與成本子計畫已草擬但未整合。你首先應做什麼？",
        "Integrate subsidiary plans into the project management plan and obtain formal approval before executing procurement",
        "將各子計畫整合成專案管理計畫，並在執行採購前取得正式核准",
        ("Authorize long-lead procurement in parallel with plan finalization", "在計畫定稿同時授權長交期採購"),
        ("Submit only the schedule plan for approval since it drives all work", "僅提交時程計畫核准，因其驅動所有工作"),
        ("Escalate to the PMO to waive approval given schedule pressure", "因時程壓力向 PMO 升級要求豁免核准"),
        ("Begin baseline work using the most complete subsidiary plan available", "依現有最完整子計畫開始基準化工作"),
        ["integrated-management", "project-management-plan", "baseline"],
    ),
    S(
        "Your agile team delivers a mobile banking feature. Mid-sprint, compliance requests a fraud-alert capability not in the sprint goal. Developers estimate it will consume most remaining capacity. What is the best approach to protect delivery while addressing the concern?",
        "你的敏捷團隊交付行動銀行功能。衝刺中期，合規單位要求未納入衝刺目標的詐欺警示能力。開發估計將耗用大部分剩餘產能。在兼顧交付與顧慮下，最佳做法是什麼？",
        "Facilitate discussion with the product owner to reprioritize the backlog and adjust the sprint through agreed agile planning practices",
        "與產品負責人促成討論，重新排序待辦清單，並僅透過雙方同意的敏捷規劃做法調整衝刺",
        ("Accept the work immediately because compliance always overrides the sprint goal", "立即接受，因合規永遠優先於衝刺目標"),
        ("Complete the sprint goal and add the notification without updating the backlog", "完成衝刺目標並在未更新待辦清單下加入通知"),
        ("Cancel the sprint and restart planning with a new team", "取消衝刺並以更換團隊方式重新規劃"),
        ("Defer compliance work until the next release train without stakeholder discussion", "在未與利害關係人討論下將合規工作延至下一發布火車"),
        ["agile-delivery", "integrated-management", "backlog-prioritization"],
    ),
    S(
        "You are tailoring a hybrid project management plan for a regulated product launch with iterative customer pilots. The PMO template is predictive-heavy. Governance requires traceability, but pilots need adaptive planning. What should the integrated plan explicitly define?",
        "你正為受法規約束且含迭代客戶試點的產品上市裁剪混合式專案管理計畫。PMO 範本偏重預測式。治理要求可追溯，但試點需要適應性規劃。整合計畫應明確定義什麼？",
        "Development approach and life cycle description for each major deliverable stream, plus change control distinguishing compliance changes from backlog reprioritization",
        "各主要可交付成果流的開發方法與生命週期描述，以及區分合規變更與待辦重排的變更控制",
        ("A single detailed Gantt chart with fixed assignments for every pilot experiment", "含每項試點固定分派的單一詳細甘特圖"),
        ("Mandatory elimination of iterative cycles once regulatory design is approved", "法規設計核准後強制取消迭代週期"),
        ("Reporting of all metrics only at project closure", "所有指標僅在專案結案時報告"),
        ("Identical change control for all work regardless of delivery approach", "不論交付方式皆採相同變更控制"),
        ["integrated-management", "hybrid", "tailoring"],
    ),
    S(
        "During planning for a predictive data-center migration, the team proposes updating subsidiary plans independently as each workstream completes its section. The sponsor wants a single integrated baseline next month. What should you recommend?",
        "在預測式資料中心遷移規劃中，團隊提議各工作流完成後獨立更新子計畫。贊助者希望下月有單一整合基準。你應建議什麼？",
        "Coordinate integrated planning sessions to consolidate subsidiary plans, resolve dependencies, and baseline the unified project management plan",
        "協調整合規劃會議，合併子計畫、解決相依性，並對統一專案管理計畫訂基準",
        ("Baseline each subsidiary plan separately as completed without cross-workstream review", "各子計畫完成即獨立訂基準，無跨工作流審查"),
        ("Delay baselining until all procurement contracts are signed", "延後訂基準直至所有採購合約簽署"),
        ("Use the most advanced workstream plan as the de facto integrated plan", "以最進度工作流計畫作為事實上整合計畫"),
        ("Skip the integrated plan and manage solely through weekly status reports", "跳過整合計畫，僅以每週狀態報告管理"),
        ["integrated-planning", "baseline", "predictive"],
    ),
    S(
        "An agile release train is starting PI planning while corporate requires a documented project management plan for audit. The ART has never produced a traditional plan. What hybrid approach best satisfies both needs?",
        "敏捷發布火車即將 PI 規劃，但企業稽核要求有文件化專案管理計畫。ART 從未產出傳統計畫。哪種混合做法最能同時滿足兩方需求？",
        "Develop a lightweight integrated plan describing PI cadence, governance checkpoints, and how team backlogs roll up to program objectives",
        "制定輕量整合計畫，描述 PI 節奏、治理檢查點，以及團隊待辦清單如何匯總至計畫目標",
        ("Convert all agile teams to waterfall for the audit period", "稽核期間將所有敏捷團隊改為瀑布"),
        ("Submit sprint backlogs as the project management plan without additional context", "僅提交衝刺待辦清單作為專案管理計畫"),
        ("Defer the audit requirement until the program completes", "延後稽核要求至計畫完成"),
        ("Create a plan that duplicates every user story in a Gantt chart", "建立將每個使用者故事複製到甘特圖的計畫"),
        ["hybrid", "integrated-management", "agile-release-train"],
    ),
]

PRC2_BASE = [
    S(
        "During a predictive ERP implementation, stakeholders disagree on whether several features belong in Phase 1. The sponsor wants a signed scope baseline before design starts. Deliverables have not been decomposed. What should you do next?",
        "在預測式 ERP 實施中，利害關係人對若干功能是否屬第一階段意見分歧。贊助者希望設計開始前簽署範疇基準。可交付成果尚未分解。你下一步應做什麼？",
        "Facilitate scope definition workshops to clarify deliverables, document exclusions, and obtain stakeholder acceptance before creating the WBS",
        "促成範疇定義工作坊以釐清可交付成果、記錄排除項目，並在建立 WBS 前取得利害關係人認可",
        ("Build the WBS immediately from the requirements document and resolve disagreements during testing", "立即依需求文件建立 WBS，測試階段再解決分歧"),
        ("Approve Phase 1 scope based on the sponsor's verbal direction", "依贊助者口頭指示核准第一階段範疇"),
        ("Defer scope decisions until the procurement contract is signed", "延後範疇決策直至採購合約簽署"),
        ("Accept all requested features in Phase 1 to avoid stakeholder conflict", "為避免衝突將所有需求功能納入第一階段"),
        ["scope-management", "wbs", "requirements"],
    ),
    S(
        "A construction project has an approved scope baseline and WBS dictionary. The architect submits a change to relocate a mechanical room affecting several work packages. No change request has been submitted. What should you do?",
        "某建案已有核准範疇基準與 WBS 詞典。建築師提交將機房移位之變更，影響多個工作包。尚未提交變更請求。你應怎麼做？",
        "Direct the team to follow perform integrated change control before implementing any scope change",
        "要求團隊在實施任何範疇變更前先遵循執行整合變更控制流程",
        ("Approve the relocation verbally and update the WBS after construction catches up", "口頭核准移位，施工趕上後再更新 WBS"),
        ("Reject the change because the scope baseline cannot be modified after approval", "拒絕變更，因範疇基準核准後不可修改"),
        ("Implement the change and absorb cost within management reserve", "直接實施變更並以管理儲備吸收成本"),
        ("Ask the contractor to proceed and document the change at project closure", "要求承包商繼續施工，結案時再記錄變更"),
        ["scope-management", "change-control", "wbs"],
    ),
    S(
        "Your agile product owner wants to validate that a released analytics module meets business needs. End users tested features during the sprint but no formal acceptance occurred. What scope validation practice should you use?",
        "你的敏捷產品負責人希望驗證已發布分析模組是否符合業務需求。使用者於衝刺中測試功能，但未正式驗收。你應採用哪種範疇驗證做法？",
        "Conduct a sprint review or release demo with stakeholders against agreed acceptance criteria and capture feedback for the backlog",
        "與利害關係人依約定驗收準則舉行衝刺審查或發布展示，並將回饋納入待辦清單",
        ("Wait until all epics are complete before any acceptance activity", "待所有史詩完成後才進行驗收"),
        ("Accept scope automatically when all automated tests pass", "自動化測試全過即自動驗收範疇"),
        ("Use the product owner's sign-off alone without stakeholder participation", "僅由產品負責人簽核，無利害關係人參與"),
        ("Defer validation until the predictive phase gate at program end", "延後驗證至計畫末期預測式階段關卡"),
        ["scope-validation", "agile", "acceptance-criteria"],
    ),
    S(
        "The product backlog for a customer portal contains 200 items with inconsistent granularity. Developers cannot estimate sprint work reliably. The next PI planning starts in two weeks. What should you do first?",
        "客戶入口網站的產品待辦清單有 200 項且粒度不一致。開發人員無法可靠估算衝刺工作。兩週後開始下一 PI 規劃。你首先應做什麼？",
        "Facilitate backlog refinement to decompose large items, clarify acceptance criteria, and establish consistent sizing before planning",
        "引導待辦清單精煉，分解大型項目、釐清驗收準則，並在規劃前建立一致估算粒度",
        ("Lock the backlog and prohibit changes until PI planning completes", "鎖定待辦清單，PI 規劃完成前禁止變更"),
        ("Estimate all 200 items in a single planning meeting regardless of readiness", "不論就緒程度，在單次規劃會估算全部 200 項"),
        ("Remove items that lack estimates to simplify the backlog", "移除未估算項目以簡化待辦清單"),
        ("Convert the backlog into a WBS and baseline it as predictive scope", "將待辦清單轉為 WBS 並作為預測式範疇基準"),
        ["product-backlog", "scope-definition", "agile"],
    ),
    S(
        "A hybrid program must trace regulatory requirements to delivered modules while agile squads iterate features. Auditors found gaps between the requirements matrix and released increments. What should you do?",
        "混合式計畫須將法規需求追溯至已交付模組，敏捷小隊則迭代功能。稽核發現需求矩陣與已發布增量間有缺口。你應怎麼做？",
        "Update the requirements traceability approach in the integrated plan and align backlog items to compliance IDs during refinement",
        "更新整合計畫中的需求追溯方法，並於精煉時將待辦項目對應合規編號",
        ("Stop agile delivery until every requirement is baselined in a predictive WBS", "暫停敏捷交付，直至所有需求在預測式 WBS 基準化"),
        ("Accept the gaps because agile teams do not use traceability matrices", "接受缺口，因敏捷團隊不使用追溯矩陣"),
        ("Remove compliance requirements from the backlog to speed delivery", "自待辦清單移除合規需求以加速交付"),
        ("Audit only at project closure without interim traceability checks", "僅在專案結案稽核，不做中期追溯檢查"),
        ["scope-management", "traceability", "hybrid"],
    ),
]

PRC3_BASE = [
    S(
        "After three releases of a subscription analytics platform, usage data shows customers rarely open advanced dashboards but heavily use export features added as an experiment. The product owner wants to reprioritize. What should you recommend?",
        "訂閱式分析平台三次發布後，數據顯示客戶很少用進階儀表板，但大量使用實驗性匯出功能。產品負責人希望重排優先序。你應建議什麼？",
        "Use validated learning from customer usage to reprioritize the backlog toward features that deliver measurable value",
        "依客戶使用情況的驗證式學習，重新排序待辦清單，聚焦可衡量價值的功能",
        ("Continue the dashboard epic because abandoning it wastes prior sprint investment", "繼續儀表板史詩，因放棄會浪費先前投入"),
        ("Freeze the backlog until finance re-approves the original business case", "凍結待辦清單直至財務重新核准原始商業案例"),
        ("Split the team so one group finishes the roadmap while another handles exports", "拆分團隊，一組完成原路線圖，另一組處理匯出"),
        ("Deliver all roadmap features before analyzing usage data", "分析使用數據前先交付所有路線圖功能"),
        ["value-delivery", "backlog-prioritization", "agile"],
    ),
    S(
        "A hybrid program combines a fixed regulatory deadline with iterative customer modules. The steering committee measures success only by regulatory submission while the business sponsor tracks NPS from modules. Teams conflict over cutting a high-value module. What should you do?",
        "混合式計畫結合固定法規截止日與迭代客戶模組。指導委員會僅以法規提交衡量成功，業務贊助者追蹤模組 NPS。團隊對是否刪減高價值模組衝突。你應怎麼做？",
        "Facilitate agreement on value measures and decision rules balancing mandatory compliance outcomes with prioritized incremental benefits",
        "促成價值衡量與決策規則共識，平衡強制合規成果與優先排序的增量效益",
        ("Defer all customer modules until regulatory submission completes regardless of business impact", "不論業務影響，將所有客戶模組延後至法規提交完成"),
        ("Let each workstream optimize locally and report independently at phase gates", "讓各工作流自行最佳化並在階段關卡獨立報告"),
        ("Rebaseline the program to a purely predictive model to eliminate iteration", "重訂基準為純預測式模式以消除迭代"),
        ("Measure success only by on-time delivery without benefit tracking", "僅以準時交付衡量成功，不追蹤效益"),
        ["value-delivery", "hybrid", "benefits-realization"],
    ),
    S(
        "Your team is planning an MVP for a telehealth platform. Stakeholders listed 40 features as must-haves. Clinical, IT, and legal each rank different features as critical. Launch funding covers three months of development. What approach best supports value-based delivery?",
        "你的團隊規劃遠距醫療平台 MVP。利害關係人列 40 項為必備。臨床、IT 與法務各自認定不同功能為關鍵。上線資金僅涵蓋三個月開發。哪種做法最能支援以價值為基礎的交付？",
        "Facilitate prioritization using value and risk criteria to define the smallest increment that delivers validated patient and provider outcomes",
        "引導以價值與風險準則排序，定義可交付已驗證病患與提供者成果的最小增量",
        ("Include all 40 features in the MVP to avoid stakeholder dissatisfaction", "MVP 納入全部 40 項以避免利害關係人不滿"),
        ("Build infrastructure first and defer all user-facing features to a later release", "先建基礎設施，所有面向使用者功能延後"),
        ("Select features randomly to accelerate decision-making", "隨機選功能以加速決策"),
        ("Wait for a complete requirements specification before defining any MVP scope", "定義 MVP 範疇前先等待完整需求規格"),
        ["mvp", "value-delivery", "prioritization"],
    ),
    S(
        "Six months after go-live of a CRM upgrade, sales productivity improved but marketing automation benefits have not materialized. The benefits owner asks whether to continue the follow-on agile stream. What should you do first?",
        "CRM 升級上線六個月後，銷售生產力提升但行銷自動化效益未顯現。效益負責人詢問是否繼續後續敏捷工作流。你首先應做什麼？",
        "Review the benefits realization plan, measure actual versus planned outcomes, and recommend data-driven adjustments to the backlog or benefits targets",
        "審查效益實現計畫，衡量實際與計畫成果，並依數據建議調整待辦清單或效益目標",
        ("Terminate the agile stream immediately because one benefit lagged", "因一項效益落後立即終止敏捷工作流"),
        ("Continue all planned features without measuring interim benefits", "不衡量中期效益，繼續所有計畫功能"),
        ("Rebaseline the business case to match current delivery without stakeholder review", "在未與利害關係人審查下重訂商業案例以符合現況交付"),
        ("Declare benefits realization complete because the CRM is operational", "因 CRM 已運作即宣告效益實現完成"),
        ["benefits-realization", "value-delivery", "measurement"],
    ),
    S(
        "An agile team uses WSJF to prioritize a platform roadmap. A low-effort regulatory item scores lower than a high-visibility feature requested by sales. Compliance deadline is eight weeks away. What should the product owner do?",
        "敏捷團隊以 WSJF 排序平台路線圖。低工作量法規項目得分低於業務部門要求的高能見度功能。合規期限八週後到期。產品負責人應怎麼做？",
        "Adjust prioritization to incorporate compliance risk and cost of delay, ensuring regulatory items meet deadlines while balancing value delivery",
        "調整排序以納入合規風險與延遲成本，確保法規項目準時完成，同時平衡價值交付",
        ("Ignore WSJF and always build sales-requested features first", "忽略 WSJF，永遠先做業務要求功能"),
        ("Complete the high-visibility feature and accept regulatory penalties if needed", "先完成高能見度功能，必要時接受法規處罰"),
        ("Stop using WSJF because it conflicts with stakeholder requests", "因與利害關係人要求衝突而停止使用 WSJF"),
        ("Escalate all prioritization decisions to the steering committee weekly", "每週將所有排序決策升級指導委員會"),
        ["value-delivery", "prioritization", "compliance"],
    ),
]

# Continue with PRC4-PRC10 in load function
MULTI_SUFFIX = {
    "PRC1": ("Select the TWO elements that should be explicitly defined in the integrated plan. (Choose 2)", "請選出兩項應在整合計畫中明確定義的元素。（選 2 項）"),
    "PRC2": ("Select the TWO actions appropriate for scope management in this situation. (Choose 2)", "請選出兩項適用於此情境的範疇管理行動。（選 2 項）"),
    "PRC3": ("Select the TWO practices that best support value-based delivery. (Choose 2)", "請選出兩項最能支援以價值為基礎交付的做法。（選 2 項）"),
    "PRC4": ("Select the TWO actions that best address resource management. (Choose 2)", "請選出兩項最能處理資源管理的行動。（選 2 項）"),
    "PRC5": ("Select the TWO activities that belong to conduct procurements. (Choose 2)", "請選出兩項屬於「實施採購」流程的活動。（選 2 項）"),
    "PRC6": ("Select the TWO correct statements about earned value in this scenario. (Choose 2)", "請選出兩項關於此情境實獲值的正確敘述。（選 2 項）"),
    "PRC7": ("Select the TWO practices that support manage quality. (Choose 2)", "請選出兩項支援「管理品質」的做法。（選 2 項）"),
    "PRC8": ("Select the TWO schedule techniques you should apply first. (Choose 2)", "請選出兩項你應優先採用的排程技巧。（選 2 項）"),
    "PRC9": ("Select the TWO actions appropriate for status evaluation. (Choose 2)", "請選出兩項適用於狀態評估的行動。（選 2 項）"),
    "PRC10": ("Select the TWO actions appropriate during close project or phase. (Choose 2)", "請選出兩項屬於「結束專案或階段」的適當行動。（選 2 項）"),
}

MULTI_SECOND = {
    "PRC1": ("Define change control procedures that distinguish compliance-driven changes from backlog reprioritization", "定義區分合規驅動變更與待辦重排的變更控制程序"),
    "PRC2": ("Document scope exclusions and obtain formal stakeholder sign-off before baselining", "記錄範疇排除項目並在訂基準前取得利害關係人正式簽核"),
    "PRC3": ("Establish measurable benefit metrics and review them at regular delivery increments", "建立可衡量效益指標並於定期交付增量審查"),
    "PRC4": ("Update the resource management plan with agreed allocations and escalation paths", "以 agreed 配置與升級路徑更新資源管理計畫"),
    "PRC5": ("Negotiate contract terms with the selected seller before award", "決標前與選定賣方議定合約條款"),
    "PRC6": ("Calculate EAC using appropriate formulas and communicate forecast variance to stakeholders", "以適當公式計算 EAC 並向利害關係人溝通預測差異"),
    "PRC7": ("Integrate automated testing and continuous integration into the delivery pipeline", "將自動化測試與持續整合納入交付管道"),
    "PRC8": ("Fast-track selected activities by performing critical tasks in parallel where dependencies allow", "在相依性允許下以平行執行關鍵任務快速追蹤選定活動"),
    "PRC9": ("Compare actual progress to baselines using earned value and trend analysis", "以實獲值與趨勢分析比較實際進度與基準"),
    "PRC10": ("Conduct a lessons learned session and update organizational process assets", "舉行經驗教訓會議並更新組織流程資產"),
}

MULTI_DISTRACTORS = [
    ("Implement changes without integrated change control to save time", "為省時在未經整合變更控制下實施變更"),
    ("Remove mandatory reviews from the critical path without approval", "未經核准自關鍵路徑移除強制審查"),
    ("Defer all planning until every uncertainty is resolved", "延後所有規劃直至每項不確定性解決"),
    ("Use verbal agreements instead of documented baselines", "以口頭協議取代文件化基準"),
    ("Report optimistic status without data to maintain stakeholder confidence", "為維持信心報告缺乏數據的樂觀狀態"),
]

EXPL_EN = {
    0: "it aligns with PMI process-domain practices by addressing root causes through proper planning, control, or governance",
    1: "it bypasses required process steps and creates rework, scope creep, or uncontrolled baseline drift",
    2: "it imposes decisions without analysis and may violate compliance, contract, or change control requirements",
    3: "it defers critical process work or misuses reserves, increasing risk to schedule, cost, or quality",
}
EXPL_ZH = {
    0: "其符合 PMI 流程領域實務，透過適當規劃、控制或治理處理根本原因",
    1: "其繞過必要流程步驟，造成返工、範疇潛變或基準失控漂移",
    2: "其在未分析下強加決策，可能違反合規、合約或變更控制要求",
    3: "其延後關鍵流程工作或誤用儲備，增加時程、成本或品質風險",
}


def load_all_scenarios():
    scenarios = {
        "PRC1": list(PRC1_BASE),
        "PRC2": list(PRC2_BASE),
        "PRC3": list(PRC3_BASE),
    }

    # PRC4 Resource management
    prc4_t = [
        ("global software rollout", "全球軟體推廣", "virtual teams", "Negotiate with functional managers to clarify priorities, adjust allocations, and update the resource management plan with escalation if conflicts persist", "與職能經理協商釐清優先序、調整配置，更新資源管理計畫；衝突持續則升級"),
        ("agile squad", "敏捷小隊", "capacity", "Work with functional managers and the product owner to protect team capacity by limiting interruptions and confirming dedicated resource commitments", "與職能經理及產品負責人合作，限制干擾並確認專責資源承諾以保護產能"),
        ("newly formed team", "新組成團隊", "Tuckman", "Facilitate team charter and norming activities, clarify roles, and monitor development stage transitions during early sprints", "引導團隊章程與規範化活動、釐清角色，並於早期衝刺監控發展階段轉換"),
        ("matrix organization", "矩陣組織", "resource-conflicts", "Analyze resource calendars, negotiate shared priorities with sponsors, and document resolution in the resource management plan", "分析資源日曆，與贊助人協商共用優先序，並於資源管理計畫記錄解決方案"),
        ("distributed team", "分散式團隊", "virtual-teams", "Establish core collaboration hours, communication protocols, and team agreements suited to multiple time zones", "建立核心協作時段、溝通協議及適應多時區的團隊協議"),
        ("critical skill gap", "關鍵技能缺口", "training", "Assess skill gaps, arrange targeted training or mentoring, and update the resource management plan with acquisition or development actions", "評估技能缺口，安排針對訓練或導師，並以取得或發展行動更新資源管理計畫"),
        ("storming phase", "震盪期", "team-development", "Coach the team through conflict resolution, reinforce working agreements, and facilitate collaboration before performance declines further", "輔導團隊衝突解決、強化工作協議，並於績效進一步下降前促進協作"),
        ("shared resource pool", "共享資源池", "allocation", "Level resources using the schedule model, escalate persistent over-allocation, and align with functional managers on priority trade-offs", "以時程模型平衡資源，對持續過度配置升級，並與職能經理對齊優先權衡"),
    ]
    scenarios["PRC4"] = []
    for ctx_en, ctx_zh, tag, ans_en, ans_zh in prc4_t:
        for v in range(3):
            scenarios["PRC4"].append(S(
                f"You are managing a {ctx_en} project. Team members report conflicting priorities and recurring bottlenecks on critical tasks. Functional managers cite budget caps. What is the most appropriate action to manage resources?",
                f"你管理{ctx_zh}專案。成員反映優先序衝突且關鍵任務反覆瓶頸。職能經理以預算上限為由。管理資源最適當的做法是什麼？",
                ans_en, ans_zh,
                ("Replace senior staff with junior resources to reduce cost", "以初階人員替換資深人員以降低成本"),
                ("Extend the schedule silently without updating the resource plan", "悄悄延長時程且不更新資源計畫"),
                ("Hire contractors immediately without procurement or plan review", "立即雇承包商，未經採購或計畫審查"),
                ("Accept over-allocation and hope teams compensate with overtime", "接受過度配置，期望團隊以加班彌補"),
                ["resource-management", tag, "matrix-organization"],
            ))

    # PRC5 Procurement
    prc5_scenarios = [
        S("Your hybrid infrastructure project must procure cloud services under a firm deadline while agile squads iterate integration. Procurement wants a three-year fixed-price contract. Technical leads need tier flexibility. What should you do before signing?",
          "混合式基礎設施專案須在固定截止日前採購雲端服務，敏捷小隊迭代整合。採購希望三年固定總價合約。技術負責人需層級彈性。簽署前你應做什麼？",
          "Analyze procurement requirements and recommend a contract structure balancing cost control with permitted scope and tier adjustments",
          "分析採購需求，建議在成本控管與允許範疇及層級調整間取得平衡的合約結構",
          ("Sign the fixed-price contract immediately to lock pricing", "立即簽固定總價合約以鎖定價格"),
          ("Delay procurement until agile squads finalize every integration detail", "延後採購直至敏捷小隊定稿所有整合細節"),
          ("Use verbal agreements and formalize after go-live", "口頭協議，上線後再正式簽約"),
          ("Select the lowest bidder without structured evaluation", "未經結構化評選即選最低價投標者"),
          ["procurement", "contracts", "hybrid"]),
        S("During source selection for a data center build, Vendor A has the lowest price but weak references. Vendor B is highest priced with strong technical scores. Vendor C is mid-priced and meets mandatory requirements. The sponsor pressures you to choose Vendor A. What should you do?",
          "資料中心建置供應商選擇中，廠商 A 最低價但參考薄弱。B 最高價但技術評分強。C 中等價格且符合強制要求。贊助者施壓選 A。你應怎麼做？",
          "Complete structured evaluation against published criteria and document the recommendation with supporting scores before any award",
          "依已公布標準完成結構化評選，決標前文件化建議與支持性評分",
          ("Award Vendor A immediately to maintain sponsor support", "立即決標 A 以維持贊助者支持"),
          ("Negotiate Vendor B to match A's price without re-scoring", "與 B 議價至 A 價格且不重新評分"),
          ("Reject all vendors and restart procurement without analysis", "拒絕所有廠商且未分析即重啟採購"),
          ("Use sole-source justification because the sponsor prefers Vendor A", "因贊助者偏好 A 而使用單一來源理由"),
          ["procurement", "source-selection", "contracts"]),
        S("Your make-or-buy analysis shows custom middleware development exceeds internal capacity but provides strategic differentiation. A vendor offers time-and-materials pricing with uncertain total cost. Finance prefers fixed-price. What should you do?",
          "自製或外購分析顯示自研中介軟體超出內部產能但具策略差異化。廠商提供總成本不確定的工時材料計價。財務偏好固定總價。你應怎麼做？",
          "Present make-or-buy results with contract type trade-offs, recommended risk-sharing structure, and cost ceiling or incentive options for decision-makers",
          "向決策者呈報自製外購結果、合約類型取捨、建議風險分攤結構及成本上限或激勵選項",
          ("Accept T&M without a not-to-exceed clause because the vendor requested it", "因廠商要求而接受無上限條款的 T&M"),
          ("Force fixed-price on the vendor without scope clarity", "在範疇不明下強迫固定總價"),
          ("Build internally regardless of capacity constraints", "不顧產能限制仍堅持自製"),
          ("Defer the decision until after implementation starts", "實施開始後再決定"),
          ["make-or-buy", "procurement", "contract-types"]),
        S("A seller on a cost-plus-fixed-fee contract reports higher-than-expected actual costs. Your team suspects inefficient practices but needs continued delivery for a regulatory milestone. What should you do?",
          "成本加固定酬金合約的賣方回報高於預期實際成本。你懷疑效率不佳但需持續交付以趕法規里程碑。你應怎麼做？",
          "Review cost documentation per contract terms, conduct procurement audits as allowed, and implement corrective actions with the seller while protecting the milestone",
          "依合約條款審查成本文件、在允許下進行採購稽核，並與賣方實施矯正措施同時保障里程碑",
          ("Terminate the contract immediately without review", "未審查即立即終止合約"),
          ("Approve all invoices without verification to maintain the relationship", "為維持關係不驗證即核准所有發票"),
          ("Convert to fixed-price mid-contract without change control", "未經變更控制即中途改固定總價"),
          ("Absorb all overruns in contingency without analysis", "未分析即以應急費吸收所有超支"),
          ["procurement", "CPFF", "contract-administration"]),
        S("Before awarding an FFP contract for a national logistics system, evaluators are assigned but no scoring sheet is approved. The sponsor wants to skip negotiations with the preferred vendor. What should you ensure is completed?",
          "決標全國物流系統固定總價合約前，評審已指派但評分表未核准。贊助者希望跳過與首選廠商議約。你應確保完成什麼？",
          "Evaluate seller proposals against documented selection criteria and negotiate contract terms before award",
          "依文件化選擇標準評估賣方提案，並於決標前議定合約條款",
          ("Develop the project charter with the external vendor", "與外部廠商共同制定專案章程"),
          ("Close all project accounts before signing", "簽約前結清所有專案帳戶"),
          ("Perform final benefits realization measurement before award", "決標前執行最終效益實現衡量"),
          ("Award based on sponsor preference without scoring", "依贊助者偏好決標，不使用評分"),
          ["procurement", "FFP", "source-selection"]),
    ]
    scenarios["PRC5"] = prc5_scenarios
    for topic, tag in [("SaaS subscription", "saas"), ("construction subcontract", "construction"), ("medical devices", "healthcare")]:
        scenarios["PRC5"].append(S(
            f"You are preparing procurement documents for a {topic} engagement with partially defined requirements. Market rates fluctuate and delivery will be iterative. Which contract approach should you recommend?",
            f"你正為需求部分定義的{topic} engagement 準備採購文件。市場價格波動且交付將迭代。你應建議哪種合約方式？",
            "Select a contract type with appropriate risk sharing—such as T&M with not-to-exceed limits or CPFF for high uncertainty—aligned to requirements maturity",
            "選擇適當風險分攤的合約類型——如含上限的 T&M 或高不確定性時的 CPFF——並與需求成熟度一致",
            ("Use FFP for all work regardless of requirements clarity", "不論需求清晰度，全部採固定總價"),
            ("Avoid written contracts and rely on purchase orders only", "避免書面合約，僅用採購單"),
            ("Delay all contracting until every requirement is finalized", "延後所有簽約直至每項需求定稿"),
            ("Let the vendor unilaterally choose contract terms", "由廠商單方面選擇合約條款"),
            ["procurement", "contract-types", tag],
        ))

    # PRC6 EVM
    prc6_evm = [
        ("BAC=500000, EV=200000, AC=220000, PV=210000", "BAC=500000、EV=200000、AC=220000、PV=210000", "CPI is below 1.0 indicating cost overrun; recommend variance analysis and corrective action per the cost management plan", "CPI 低於 1.0 表示成本超支；依成本管理計畫建議差異分析與矯正行動"),
        ("BAC=1200000, EV=600000, AC=540000, PV=580000", "BAC=1200000、EV=600000、AC=540000、PV=580000", "SPI is below 1.0 indicating schedule slippage; update forecasts and evaluate schedule compression options per the plan", "SPI 低於 1.0 表示時程落後；更新預測並依計畫評估時程壓縮選項"),
        ("BAC=800000, EV=400000, AC=400000, PV=400000", "BAC=800000、EV=400000、AC=400000、PV=400000", "Performance is on plan at the measurement date; continue monitoring trends and validate remaining work estimates", "於衡量日績效符合計畫；持續監控趨勢並驗證剩餘工作估算"),
        ("BAC=2000000, EV=900000, AC=1100000, PV=1000000", "BAC=2000000、EV=900000、AC=1100000、PV=1000000", "Calculate EAC assuming current CPI continues, communicate forecast overrun, and propose recovery options through change control", "假設現有 CPI 持續，計算 EAC、溝通預測超支，並透過變更控制提出追回方案"),
    ]
    scenarios["PRC6"] = []
    for evm, evm_zh, ans_en, ans_zh in prc6_evm:
        for pct in [40, 55, 70]:
            scenarios["PRC6"].append(S(
                f"At {pct}% completion of a predictive software program, earned value data shows {evm}. The steering committee meets tomorrow. What should you report and recommend?",
                f"預測式軟體計畫完成 {pct}% 時，實獲值數據顯示 {evm_zh}。指導委員會明日開會。你應報告並建議什麼？",
                ans_en, ans_zh,
                ("Report green status because work is progressing", "因工作進行中而報告綠燈狀態"),
                ("Request additional budget without variance analysis", "未做差異分析即要求追加預算"),
                ("Rebaseline immediately without stakeholder approval", "未經利害關係人核准即立即重訂基準"),
                ("Stop EVM reporting and use percent complete only", "停止 EVM 報告，僅用完成百分比"),
                ["earned-value", "EVM", "forecasting"],
            ))
    scenarios["PRC6"].extend([
        S("Your project has BAC=$1M, EV=$450K, AC=$500K. The sponsor asks for ETC assuming future work will perform at the current CPI. Which formula applies?",
          "專案 BAC=100 萬、EV=45 萬、AC=50 萬。贊助者要求假設後續工作依現有 CPI 績效的 ETC。適用哪個公式？",
          "EAC = BAC / CPI; ETC = EAC - AC, using CPI = EV / AC",
          "EAC = BAC / CPI；ETC = EAC - AC，其中 CPI = EV / AC",
          ("EAC = AC + BAC - EV regardless of trends", "不論趨勢皆用 EAC = AC + BAC - EV"),
          ("ETC = BAC - EV without considering cost performance", "ETC = BAC - EV，不考慮成本績效"),
          ("VAC = EV - AC for remaining work forecasting", "以 VAC = EV - AC 預測剩餘工作"),
          ("TCPI = EV / AC for schedule recovery", "以 TCPI = EV / AC 追回時程"),
          ["EVM", "EAC", "CPI"]),
        S("Management asks whether the remaining work can be completed within the remaining budget. CPI=0.85, BAC=$2M, EV=$800K, AC=$940K. What index should you calculate?",
          "管理層詢問剩餘工作能否在剩餘預算內完成。CPI=0.85、BAC=200 萬、EV=80 萬、AC=94 萬。你應計算哪個指標？",
          "TCPI to complete within BAC = (BAC - EV) / (BAC - AC) and compare to current CPI",
          "以 BAC 完工 TCPI = (BAC - EV) / (BAC - AC) 並與現有 CPI 比較",
          ("SPI only, because budget questions are schedule-related", "僅 SPI，因預算問題與時程相關"),
          ("CPI squared to estimate future performance", "CPI 平方估算未來績效"),
          ("Percent complete without earned value", "不用實獲值，僅用完成百分比"),
          ("VAC divided by remaining duration", "VAC 除以剩餘工期"),
          ["EVM", "TCPI", "budget-management"]),
    ])

    # PRC7 Quality
    prc7_t = [
        ("control chart", "管制圖", "Monitor the control chart for out-of-control signals, investigate special-cause variation, and implement corrective actions per the quality management plan", "監控管制圖的失控訊號，調查特殊原因變異，並依品質管理計畫實施矯正行動"),
        ("DMAIC", "DMAIC", "Facilitate a structured improvement cycle defining the problem, measuring baseline, analyzing root causes, improving the process, and controlling gains", "引導結構化改善循環：定義問題、衡量基準、分析根本原因、改善流程並控制成果"),
        ("quality audit", "品質稽核", "Conduct the audit per the quality management plan, document findings, and track corrective actions to closure", "依品質管理計畫執行稽核、記錄發現並追蹤矯正行動至結案"),
        ("Definition of Done", "完成定義", "Review and enforce the Definition of Done linked to non-functional requirements before accepting increments", "審查並執行連結非功能需求的完成定義，再驗收增量"),
        ("inspection vs prevention", "檢驗與預防", "Shift toward prevention by integrating quality practices into development rather than relying on end-phase inspection alone", "將品質實務整合至開發以轉向預防，而非僅依末期檢驗"),
        ("continuous improvement", "持續改善", "Use retrospective and quality metrics to identify improvement actions and update team agreements", "以回顧與品質指標識別改善行動並更新團隊協議"),
    ]
    scenarios["PRC7"] = []
    for method_en, method_zh, ans_en, ans_zh in prc7_t:
        for ctx in ["pharmaceutical packaging", "e-commerce platform", "public transit app"]:
            ctx_zh = {"pharmaceutical packaging": "藥品包裝", "e-commerce platform": "電商平台", "public transit app": "大眾運輸 App"}[ctx]
            scenarios["PRC7"].append(S(
                f"During delivery of a {ctx}, quality metrics show increasing defect rates. The team debates whether to add a final inspection phase. Your quality management plan emphasizes {method_en.replace('_', ' ')}. What should you do?",
                f"交付{ctx_zh}期間，品質指標顯示缺陷率上升。團隊爭論是否增加最終檢驗階段。品質管理計畫強調{method_zh}。你應怎麼做？",
                ans_en, ans_zh,
                ("Add inspection headcount without changing the process", "不改流程，僅增加檢驗人力"),
                ("Accept higher defect rates to protect the schedule", "為保時程接受較高缺陷率"),
                ("Skip quality reviews until after customer release", "客戶發布前跳過品質審查"),
                ("Blame the vendor without root-cause analysis", "未做根本原因分析即归咎廠商"),
                ["quality-management", method_en.replace(" ", "-"), "process-improvement"],
            ))

    # PRC8 Schedule
    prc8_t = [
        ("critical path", "關鍵路徑", "Analyze the schedule network to confirm critical path activities and focus recovery efforts where float is zero", "分析時程網路確認關鍵路徑活動，將追回努力聚焦於浮時為零之處"),
        ("fast-tracking", "快速追蹤", "Fast-track selected activities by performing them in parallel where dependencies allow, after risk review", "風險審查後，在相依性允許下平行執行選定活動以快速追蹤"),
        ("crashing", "趕工", "Crash critical-path activities by adding approved resources after analyzing cost and risk trade-offs", "分析成本與風險權衡後，以增派核准資源趕工關鍵路徑活動"),
        ("PERT", "PERT", "Use three-point estimates for uncertain activities and recalculate expected duration through the schedule model", "對不確定活動使用三點估算，並透過時程模型重算期望工期"),
        ("Kanban WIP limits", "Kanban 在製限制", "Apply WIP limits and flow metrics to reduce bottlenecks and improve predictable delivery on the agile stream", "套用 WIP 限制與流動指標，減少瓶頸並提升敏捷工作流可預測交付"),
        ("total float", "總浮時", "Identify activities with float and assess whether resequencing non-critical work can free resources for critical tasks", "識別有浮時活動，評估重排非關鍵工作是否可釋出資源支援關鍵任務"),
    ]
    scenarios["PRC8"] = []
    for method_en, method_zh, ans_en, ans_zh in prc8_t:
        for delay in [3, 5, 8]:
            scenarios["PRC8"].append(S(
                f"A hybrid program must recover {delay} weeks on a committed milestone while continuing iterative releases. The schedule management plan allows compression with risk review. After updating the schedule model, what should you apply first regarding {method_en.replace('_', ' ')}?",
                f"混合式計畫須在承諾里程碑追回 {delay} 週，同時維持迭代發布。時程管理計畫允許風險審查下壓縮。更新時程模型後，關於{method_zh}你應優先採用什麼？",
                ans_en, ans_zh,
                ("Remove compliance activities from the schedule without change control", "未經變更控制自時程移除合規活動"),
                ("Delete buffer tasks to show an earlier finish date", "刪除緩衝任務以顯示較早完工日"),
                ("Extend releases to quarterly cycles without stakeholder assessment", "未評估利害關係人即將發布延長為每季"),
                ("Report an earlier date without changing activity logic", "不改變活動邏輯即報告較早日期"),
                ["schedule-management", method_en.replace(" ", "-"), "CPM"],
            ))

    # PRC9 Status evaluation
    prc9_t = [
        ("earned value trends", "實獲值趨勢", "Present CPI and SPI trends with variance analysis and recommended corrective actions at the project review", "於專案審查呈報 CPI 與 SPI 趨勢、差異分析與建議矯正行動"),
        ("sprint review metrics", "衝刺審查指標", "Evaluate working product against iteration goals and use velocity trends to forecast release completion", "依迭代目標評估可運作產品，並以速率趨勢預測發布完成"),
        ("milestone assessment", "里程碑評估", "Compare actual milestone completion to the baseline schedule and escalate variances per the management plan", "比較實際里程碑完成與基準時程，依管理計畫升級差異"),
        ("risk-adjusted forecast", "風險調整預測", "Integrate risk register impacts into status reporting and update forecasts with explicit assumptions", "將風險登錄影響納入狀態報告，並以明確假設更新預測"),
        ("benefits tracking", "效益追蹤", "Report delivery status alongside benefits realization metrics to show value progress, not just task completion", "報告交付狀態時並陳效益實現指標，展現價值進度而非僅任務完成"),
    ]
    scenarios["PRC9"] = []
    for topic_en, topic_zh, ans_en, ans_zh in prc9_t:
        for v in range(4):
            scenarios["PRC9"].append(S(
                f"You are preparing for a monthly project performance review. Stakeholders complained that prior reports showed activity completion but masked schedule and cost issues. You need to improve status evaluation using {topic_en.replace('_', ' ')}. What should you do?",
                f"你正準備每月專案績效審查。利害關係人抱怨先前報告顯示活動完成卻掩蓋時程與成本問題。你需以{topic_zh}改善狀態評估。你應怎麼做？",
                ans_en, ans_zh,
                ("Report only green metrics to maintain confidence", "僅報告綠燈指標以維持信心"),
                ("Delay the review until all variances are resolved", "延後審查直至所有差異解決"),
                ("Use percent complete without connecting to baselines", "使用完成百分比但不連結基準"),
                ("Exclude agile team data from the integrated report", "整合報告排除敏捷團隊數據"),
                ["status-evaluation", topic_en.replace(" ", "-"), "project-reviews"],
            ))

    # PRC10 Closure
    prc10_scenarios = [
        S("Your predictive infrastructure project received final acceptance from the sponsor. Operations confirmed transition, but vendor invoices, archive indexing, and lessons learned are pending. HR needs confirmation before reassigning team members. What should you do?",
          "預測式基礎設施專案已獲贊助者最終驗收。營運已確認移交，但廠商發票、歸檔索引與經驗教訓仍待完成。人資需在重新分派成員前收到確認。你應怎麼做？",
          "Complete administrative closure activities including finalizing archives, capturing lessons learned, and releasing resources per the closure plan",
          "依結案計畫完成行政結案活動，包括定稿歸檔、擷取經驗教訓與釋出資源",
          ("Reopen the scope baseline to add enhancement requests from acceptance", "重開範疇基準以加入驗收期間強化需求"),
          ("Issue a new charter for the same deliverables under a different name", "以不同名稱為相同可交付成果發布新章程"),
          ("Begin phase two planning without closing phase one records", "未結案第一階段紀錄即開始第二階段規劃"),
          ("Release all team members immediately without final reporting", "未完成最終報告即立即釋出所有成員"),
          ["project-closure", "lessons-learned", "administrative-closure"]),
        S("An agile product reached end-of-life. The team completed the final release retrospective but has not archived repositories or updated OPAs. Support teams lack runbooks. What closure actions remain?",
          "敏捷產品達到生命週期終點。團隊完成最終發布回顧，但未歸檔儲存庫或更新 OPA。支援團隊缺乏 runbook。尚余哪些結案行動？",
          "Archive project artifacts, finalize operational handoff documentation, update organizational process assets, and obtain formal acceptance where required",
          "歸檔專案產出、定稿營運交接文件、更新組織流程資產，並在需要時取得正式驗收",
          ("Skip archival because agile projects do not require documentation", "因敏捷專案不需文件而跳過歸檔"),
          ("Transfer all work to a new team without closure records", "無結案紀錄即移交新團隊"),
          ("Delete repositories to reduce storage costs", "為降低儲存成本刪除儲存庫"),
          ("Close only financial accounts and ignore knowledge transfer", "僅結清財務帳戶，忽略知識移轉"),
          ["project-closure", "opas", "final-reporting"]),
    ]
    scenarios["PRC10"] = prc10_scenarios
    for ctx, ctx_zh in [("ERP phase 1", "ERP 第一階段"), ("mobile app program", "行動 App 計畫"), ("construction handover", "建案移交")]:
        for v in range(5):
            scenarios["PRC10"].append(S(
                f"You are closing {ctx}. Final deliverables are accepted but procurement closeout, contract archives, and lessons learned workshop are incomplete. What is the appropriate next step?",
                f"你正結案{ctx_zh}。最終可交付成果已驗收，但採購結案、合約歸檔與經驗教訓工作坊尚未完成。適當的下一步是什麼？",
                "Execute the close project or phase process: finalize financial and procurement records, archive documents, conduct lessons learned, and release resources",
                "執行結束專案或階段流程：定稿財務與採購紀錄、歸檔文件、舉行經驗教訓並釋出資源",
                ("Start a new project for enhancements without closing current records", "未結案現有紀錄即啟動強化新專案"),
                ("Mark the project closed in email without administrative activities", "以電郵標記結案，不做行政活動"),
                ("Retain all team members indefinitely for potential support", "無限期保留所有成員以備支援"),
                ("Discard draft lessons learned to accelerate closure", "為加速結案丟棄草稿經驗教訓"),
                ["project-closure", "final-reporting", "administrative-closure"],
            ))

    # Expand PRC1-3 with templates
    prc1_t = [
        ("iterative planning cadence", "迭代規劃節奏", "Define rolling-wave planning horizons and integration points in the project management plan", "於專案管理計畫定義滾動式規劃視野與整合點"),
        ("subsidiary plan integration", "子計畫整合", "Schedule integrated planning workshops to consolidate subsidiary plans before baseline approval", "安排整合規劃工作坊，於基準核准前合併子計畫"),
        ("change-driven replanning", "變更驅動重規劃", "Trigger replanning through integrated change control when approved changes affect multiple baselines", "當核准變更影響多個基準時，透過整合變更控制觸發重規劃"),
    ]
    for t_en, t_zh, a_en, a_zh in prc1_t:
        for i in range(6):
            scenarios["PRC1"].append(S(
                f"You are developing the project management plan for a hybrid digital transformation. Teams disagree on how {t_en} should work across predictive and agile streams. What should the integrated plan address?",
                f"你正為混合式數位轉型制定專案管理計畫。團隊對{t_zh}在預測與敏捷工作流間如何運作意見分歧。整合計畫應處理什麼？",
                a_en, a_zh,
                ("Allow each team to plan independently without integration", "各團隊獨立規劃，無需整合"),
                ("Use only the PMO template without tailoring", "僅用 PMO 範本，不裁剪"),
                ("Defer planning until all requirements are known", "延後規劃直至所有需求已知"),
                ("Baseline only the schedule and ignore other knowledge areas", "僅對時程訂基準，忽略其他知識領域"),
                ["integrated-planning", "hybrid", "project-management-plan"],
            ))

    prc2_t = [
        ("WBS decomposition", "WBS 分解", "Decompose deliverables into work packages with WBS dictionary entries before baseline", "訂基準前將可交付成果分解為工作包並建立 WBS 詞典"),
        ("scope creep", "範疇潛變", "Refer unauthorized requests to integrated change control and update the backlog or baseline only when approved", "將未授權請求導向整合變更控制，僅於核准後更新待辦或基準"),
        ("acceptance criteria", "驗收準則", "Validate deliverables against documented acceptance criteria with stakeholder participation", "與利害關係人依文件化驗收準則驗證可交付成果"),
    ]
    for t_en, t_zh, a_en, a_zh in prc2_t:
        for i in range(6):
            scenarios["PRC2"].append(S(
                f"During a product delivery effort, the team struggles with {t_en}. Stakeholders add requests informally and traceability gaps appear. What should you do?",
                f"產品交付期間，團隊在{t_zh}上遇困難。利害關係人非正式新增請求且出現追溯缺口。你應怎麼做？",
                a_en, a_zh,
                ("Accept informal additions to maintain stakeholder goodwill", "為維持關係接受非正式新增"),
                ("Freeze all scope permanently at the first baseline", "第一次基準後永久凍結範疇"),
                ("Remove traceability to speed delivery", "移除追溯以加速交付"),
                ("Implement changes immediately when requested by executives", "高階要求時立即實施變更"),
                ["scope-management", "wbs", "change-control"],
            ))

    prc3_t = [
        ("MVP scope", "MVP 範疇", "Define MVP scope using value, risk, and learning goals rather than full feature lists", "以價值、風險與學習目標定義 MVP 範疇，而非完整功能清單"),
        ("benefit metrics", "效益指標", "Track benefit metrics at each release and adjust the roadmap based on realized outcomes", "每次發布追蹤效益指標，並依實現成果調整路線圖"),
        ("cost of delay", "延遲成本", "Prioritize backlog items considering cost of delay and compliance deadlines alongside business value", "排序待辦時同時考量延遲成本、合規期限與業務價值"),
    ]
    for t_en, t_zh, a_en, a_zh in prc3_t:
        for i in range(6):
            scenarios["PRC3"].append(S(
                f"Leadership asks how {t_en} will be managed on your value-driven program. Teams default to building complete specifications before releasing anything. What should you recommend?",
                f"領導詢問你的價值導向計畫如何管理{t_zh}。團隊預設在發布前先完成全部規格。你應建議什麼？",
                a_en, a_zh,
                ("Deliver the full specification in a single release", "單次發布交付完整規格"),
                ("Ignore business value and optimize for technical completeness", "忽略業務價值，優化技術完整度"),
                ("Stop measuring outcomes after initial launch", "初次上線後停止衡量成果"),
                ("Defer all prioritization to external vendors", "所有排序延後給外部廠商"),
                ["value-delivery", "mvp", "benefits-realization"],
            ))

    return scenarios


SCENARIOS = load_all_scenarios()


def distribute(count, weights):
    total = sum(weights)
    raw = [count * w / total for w in weights]
    result = [int(r) for r in raw]
    remainder = count - sum(result)
    fractions = [(i, raw[i] - result[i]) for i in range(len(weights))]
    fractions.sort(key=lambda x: -x[1])
    for i in range(remainder):
        result[fractions[i][0]] += 1
    return result


def build_explanation(correct_idx, is_multi=False, correct_indices=None, n_opts=4):
    letters = "ABCDE"
    if is_multi:
        correct_set = set(correct_indices)
        parts_en, parts_zh = [], []
        for i in range(n_opts):
            if i in correct_set:
                parts_en.append(f"Option {letters[i]} is correct because it applies appropriate process management practices aligned with the scenario requirements.")
                parts_zh.append(f"選項 {letters[i]} 正確，因其套用符合情境需求的適當流程管理實務。")
            else:
                parts_en.append(f"Option {letters[i]} is incorrect because it bypasses required controls, creates unapproved baseline changes, or fails to address the process gap.")
                parts_zh.append(f"選項 {letters[i]} 錯誤，因其繞過必要控制、造成未核准基準變更或未處理流程缺口。")
        return " ".join(parts_en), " ".join(parts_zh)
    parts_en = ["Option " + letters[correct_idx] + " is correct because " + EXPL_EN[0] + "."]
    parts_zh = ["選項 " + letters[correct_idx] + " 正確，因為" + EXPL_ZH[0] + "。"]
    wrong_reasons_en = [EXPL_EN[1], EXPL_EN[2], EXPL_EN[3]]
    wrong_reasons_zh = [EXPL_ZH[1], EXPL_ZH[2], EXPL_ZH[3]]
    wi = 0
    for i in range(n_opts):
        if i != correct_idx:
            parts_en.append(f"Option {letters[i]} is incorrect because {wrong_reasons_en[wi % 3]}.")
            parts_zh.append(f"選項 {letters[i]} 錯誤，因為{wrong_reasons_zh[wi % 3]}。")
            wi += 1
    return " ".join(parts_en), " ".join(parts_zh)


def make_mcq(qid, task, approach, difficulty, scenario):
    stem_en, stem_zh, correct_en, correct_zh, distractors, tags = scenario
    options = [{"en": correct_en, "zh": correct_zh}]
    for d_en, d_zh in distractors:
        options.append({"en": d_en, "zh": d_zh})
    indices = list(range(4))
    random.Random(qid).shuffle(indices)
    shuffled = [options[i] for i in indices]
    correct = indices.index(0)
    exp_en, exp_zh = build_explanation(correct)
    return {
        "id": qid, "type": "mcq", "domain": "process", "task": task,
        "approach": approach, "difficulty": difficulty,
        "stem": {"en": stem_en, "zh": stem_zh},
        "options": shuffled, "correct": correct,
        "explanation": {"en": exp_en, "zh": exp_zh}, "tags": tags,
    }


def make_multi(qid, task, approach, difficulty, scenario, idx):
    stem_en, stem_zh, correct_en, correct_zh, distractors, tags = scenario
    suffix_en, suffix_zh = MULTI_SUFFIX[task]
    second_en, second_zh = MULTI_SECOND[task]
    correct_opts = [{"en": correct_en, "zh": correct_zh}, {"en": second_en, "zh": second_zh}]
    wrong = [{"en": d[0], "zh": d[1]} for d in distractors[:2]]
    extra = [{"en": d[0], "zh": d[1]} for d in MULTI_DISTRACTORS[idx % len(MULTI_DISTRACTORS): idx % len(MULTI_DISTRACTORS) + 3]]
    while len(extra) < 3:
        d = MULTI_DISTRACTORS[len(extra) % len(MULTI_DISTRACTORS)]
        extra.append({"en": d[0], "zh": d[1]})
    all_opts = (correct_opts + wrong + extra)[:5]
    indices = list(range(len(all_opts)))
    random.Random(qid + "_m").shuffle(indices)
    shuffled = [all_opts[i] for i in indices]
    correct_indices = sorted([indices.index(0), indices.index(1)])
    exp_en, exp_zh = build_explanation(0, is_multi=True, correct_indices=correct_indices, n_opts=5)
    return {
        "id": qid, "type": "multi", "domain": "process", "task": task,
        "approach": approach, "difficulty": difficulty,
        "stem": {"en": stem_en + " " + suffix_en, "zh": stem_zh + suffix_zh},
        "options": shuffled, "correct": correct_indices, "selectN": 2,
        "explanation": {"en": exp_en, "zh": exp_zh}, "tags": tags,
    }


def assign_attributes(count):
    task_counts = distribute(count, [1] * 10)
    approach_counts = distribute(count, APPROACH_WEIGHTS)
    diff_counts = distribute(count, DIFF_WEIGHTS)
    multi_count = round(count * 0.12)
    mcq_count = count - multi_count
    tasks = [TASKS[i] for i, c in enumerate(task_counts) for _ in range(c)]
    approaches = [APPROACHES[i] for i, c in enumerate(approach_counts) for _ in range(c)]
    diffs = [DIFFICULTIES[i] for i, c in enumerate(diff_counts) for _ in range(c)]
    types = [False] * mcq_count + [True] * multi_count
    combined = list(zip(tasks, approaches, diffs, types))
    random.Random(42).shuffle(combined)
    return combined


def generate_file(filename, start_num, end_num):
    count = end_num - start_num + 1
    attrs = assign_attributes(count)
    questions = []
    task_counters = {t: 0 for t in TASKS}
    for i, num in enumerate(range(start_num, end_num + 1)):
        qid = f"PRC-{num:04d}"
        task, approach, difficulty, is_multi = attrs[i]
        scenarios = SCENARIOS[task]
        idx = task_counters[task] % len(scenarios)
        task_counters[task] += 1
        scenario = scenarios[idx]
        if is_multi:
            q = make_multi(qid, task, approach, difficulty, scenario, idx)
        else:
            q = make_mcq(qid, task, approach, difficulty, scenario)
        questions.append(q)
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return filepath, len(questions)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for filename, start, end in FILES:
        path, n = generate_file(filename, start, end)
        print(f"Wrote {n} questions to {path.name}")
        total += n
    print(f"Total: {total} questions")
    for t in TASKS:
        print(f"  {t}: {len(SCENARIOS[t])} scenarios in bank")


if __name__ == "__main__":
    main()
