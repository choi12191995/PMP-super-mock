#!/usr/bin/env python3
"""Generate PMP People domain questions PPL-0021 through PPL-0592."""

import json
import random
from itertools import cycle
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "public" / "questions"
random.seed(20260718)

FILES = [
    ("people-02.json", 21, 120),
    ("people-03.json", 121, 220),
    ("people-04.json", 221, 320),
    ("people-05.json", 321, 420),
    ("people-06.json", 421, 520),
    ("people-07.json", 521, 592),
]

TASKS = [f"PPL{i}" for i in range(1, 9)]

APPROACHES = ["predictive", "agile", "hybrid"]
APPROACH_WEIGHTS = [40, 30, 30]
DIFFICULTIES = [1, 2, 3]
DIFF_WEIGHTS = [25, 50, 25]

# Each scenario: stem_en, stem_zh, correct_en, correct_zh, distractors[(en,zh)x4], tags
# Multi scenarios add: multi_correct_indices (list of 2 from 0-4), multi_stem_suffix

def S(stem_en, stem_zh, correct_en, correct_zh, d1, d2, d3, d4, tags):
    return (stem_en, stem_zh, correct_en, correct_zh,
            [d1, d2, d3, d4], tags)

SCENARIOS = {
"PPL1": [
    S("You are the project manager for a regional healthcare network modernization. Clinical directors, IT, and finance leaders interpret the program goal differently—some focus on patient throughput, others on cost reduction. Delivery teams receive conflicting priorities weekly. What should you do FIRST to build a common vision?",
      "您是區域醫療網現代化計畫的專案經理。臨床主任、資訊與財務主管對計畫目標理解不同。交付團隊每週收到衝突優先順序。為建立共同願景，您首先應做什麼？",
      "Facilitate a vision workshop where stakeholders co-create objectives, measurable outcomes, and guiding principles documented in a team charter.",
      "主持願景工作坊，引導利害關係人共同制定目標、可衡量成果與指導原則，並記錄於團隊章程。",
      ("Issue a detailed WBS so teams stop debating goals and start executing.", "發布詳細 WBS，讓團隊停止辯論目標並開始執行。"),
      ("Ask the sponsor to mandate cost reduction over all clinical objectives.", "請發起人下令成本削減優先於所有臨床目標。"),
      ("Delay vision alignment until the requirements specification is legal-approved.", "延後願景對齊，直至需求規格獲法務核准。"),
      ("Assign each department to develop independent vision statements.", "指派各部門獨立制定願景聲明。"),
      ["common-vision", "team-charter", "facilitation"]),
    S("You are leading a hybrid IoT platform program across manufacturing plants. Predictive infrastructure teams follow stage gates while agile squads iterate on analytics. Plant managers and corporate strategy disagree on whether uptime or innovation should headline the vision. What is the BEST alignment approach?",
      "您領導跨廠區 IoT 混合式計畫。基礎設施採預測式關卡，分析小隊敏捷迭代。廠區經理與企業策略對願景應強調稼動率或創新分歧。最佳對齊做法為何？",
      "Conduct a hybrid alignment session linking OKRs to reliability metrics and innovation outcomes, then publish a shared team charter.",
      "舉辦混合對齊會議，將 OKR 連結可靠度指標與創新成果，並發布共用團隊章程。",
      ("Let each plant define its own vision to preserve local autonomy.", "讓各廠區獨立定義願景以保留在地自主。"),
      ("Finalize the predictive schedule first and revisit vision after gate one.", "先完成預測式時程，第一次關卡後再討論願景。"),
      ("Direct agile squads to pause until infrastructure completes all gates.", "指示敏捷小隊暫停，直至基礎設施完成所有關卡。"),
      ("Escalate to HR without structured stakeholder input.", "在未結構化利害關係人投入下升級至人資。"),
      ["hybrid-alignment", "OKR", "team-charter"]),
    S("You are the PM for a university digital campus initiative. Faculty, students, and administration returned incompatible success definitions from separate surveys. The sponsor expects a unified roadmap within two weeks. What should you do?",
      "您是大学數位校園計畫 PM。教師、學生與行政分別調查後提出不相容成功定義。發起人期望兩週內有統一路線圖。您應怎麼做？",
      "Organize a facilitated vision workshop with representatives to synthesize shared objectives and draft OKRs for executive confirmation.",
      "組織代表利害關係人的引導式願景工作坊，綜合共同目標並草擬 OKR 供高階確認。",
      ("Average survey responses mathematically as the official vision.", "以數學平均調查回覆作為正式願景。"),
      ("Adopt administration's vision since they control budget.", "採納行政願景，因其掌控預算。"),
      ("Wait for next academic year planning before alignment.", "等待下一學年規劃再對齊。"),
      ("Hire a vendor to build while vision discussions continue.", "聘廠商建置，願景討論平行進行。"),
      ["vision-workshop", "OKR", "stakeholder-alignment"]),
    S("You are managing a corporate ESG reporting program. Teams use different terminology for the same metrics, confusing executive briefings. What action BEST establishes a common vision?",
      "您管理企業 ESG 報告計畫。團隊對相同指標用不同術語，高階簡報混淆。哪項行動最能建立共同願景？",
      "Facilitate a cross-functional workshop to agree on shared terminology, success measures, and a program charter linking ESG goals to business outcomes.",
      "引導跨職能工作坊，就共用術語、成功衡量及連結 ESG 與業務成果的計畫章程達成共識。",
      ("Publish a glossary unilaterally without workshops.", "單方面發布詞彙表，不舉辦工作坊。"),
      ("Defer terminology alignment until after the first filing deadline.", "延後術語對齊至首次申報截止後。"),
      ("Allow each function to report using preferred definitions.", "允許各職能以偏好定義回報。"),
      ("Focus on data collection and address vision at closeout.", "專注資料收集，願景留待收尾。"),
      ["common-vision", "team-charter", "ESG"]),
    S("You are the PM for a merger integration program. Legacy and acquiring firm leaders hold different assumptions about cultural priorities and integration speed. Workstreams started without a shared north star. What should you do FIRST?",
      "您是併購整合 PM。被併與收購方對文化優先與整合速度假設不同。工作流已在缺乏共同北極星下啟動。您首先應做什麼？",
      "Pause to facilitate a vision workshop with key leaders from both organizations to define integration principles, success criteria, and a shared team charter.",
      "暫停並引導兩組織關鍵領導人參與願景工作坊，定義整合原則、成功準則與共用團隊章程。",
      ("Accelerate delivery to demonstrate progress before addressing culture.", "加速交付展現進度，文化稍後處理。"),
      ("Implement acquiring company vision by executive decree.", "以高階命令實施收購方願景。"),
      ("Outsource planning to consultants without internal sessions.", "外包規劃給顧問，無內部會議。"),
      ("Create separate vision documents per business unit.", "各事業單位分別制定願景文件。"),
      ["vision-workshop", "merger-integration", "team-charter"]),
    S("You are the PM launching a public transit smart-ticketing program. City council, operators, and vendors propose different visions at kickoff. The contract start date is fixed. What is the MOST appropriate first step?",
      "您是公共運輸智慧票證 PM。市議會、營運商與廠商啟動時提出不同願景。合約開始日已固定。最適當第一步為何？",
      "Schedule a structured vision workshop in the first planning window to align stakeholders on passenger experience goals and document them in a team charter.",
      "在首個規劃窗口安排結構化願景工作坊，就乘客體驗目標對齊並記錄於團隊章程。",
      ("Begin vendor development and resolve vision at UAT.", "立即開始開發，願景留待驗收解決。"),
      ("Accept the vendor proposal as the program vision.", "採納廠商提案為計畫願景。"),
      ("Request a six-month extension before vision discussions.", "願景討論前先申請六個月展延。"),
      ("Limit vision input to city council only.", "願景投入僅限市議會。"),
      ["vision-workshop", "public-sector", "team-charter"]),
    S("You are leading a hybrid cloud migration. Infrastructure follows waterfall milestones while application teams use Scrum. Leadership OKRs emphasize cost savings but product teams optimize velocity. What should you do to reconcile these into one vision?",
      "您領導混合雲遷移。基礎設施依瀑布里程碑、應用團隊用 Scrum。領導 OKR 強調成本，產品團隊優化速度。如何整合為單一願景？",
      "Facilitate hybrid alignment to map OKRs across workstreams, agree on balanced success measures, and update the team charter with shared priorities.",
      "引導混合對齊，將 OKR 對應各工作流，就平衡成功衡量達成共識，並以共同優先順序更新團隊章程。",
      ("Prioritize cost OKRs for infrastructure only.", "基礎設施僅優先成本 OKR。"),
      ("Remove OKRs and manage by velocity alone.", "移除 OKR，僅以速度管理。"),
      ("Wait until migration completes to define shared measures.", "待遷移完成再定義共用衡量。"),
      ("Let the CFO unilaterally set vision from financial targets.", "讓財務長依財務目標單方面定願景。"),
      ["hybrid-alignment", "OKR", "cloud-migration"]),
    S("You are the PM for a nonprofit expanding food-security services across three counties. Volunteers, donors, and officials define success differently. Funding is secured but teams lack direction. What should you do FIRST?",
      "您是非營利跨三縣糧食安全服務 PM。志工、捐助者與縣府對成功定義不同。資金到位但團隊缺方向。您首先應做什麼？",
      "Facilitate a vision workshop with representatives to define shared impact goals and document measurable OKRs in a program charter.",
      "引導各群代表願景工作坊，定義共同影響目標並以可衡量 OKR 記錄於計畫章程。",
      ("Track only meals served as the easiest metric.", "僅追蹤供餐數。"),
      ("Defer vision until after a six-month county pilot.", "延後願景至六個月試點後。"),
      ("Let each county operate without a shared vision.", "各縣獨立運作，無共用願景。"),
      ("Focus on fundraising and align strategy at year-end.", "專注募款，年底再對齊策略。"),
      ["vision-workshop", "OKR", "nonprofit"]),
    S("You are the PM for an AI ethics governance framework. Legal, data science, and business leaders champion different ethical priorities. Policy drafts contradict each other. What is the BEST initial action?",
      "您是 AI 倫理治理框架 PM。法務、資料科學與事業單位主管倡導不同倫理優先。政策草案互相矛盾。最佳初始行動為何？",
      "Conduct a vision workshop to establish shared ethical principles, success criteria, and a team charter guiding policy development.",
      "舉辦願景工作坊，建立共用倫理原則、成功準則及指導政策制定的團隊章程。",
      ("Publish legal's draft as final policy for compliance deadlines.", "發布法務草案為最終政策。"),
      ("Let data scientists define ethics by model accuracy alone.", "僅依模型準確度讓資料科學定倫理標準。"),
      ("Postpone policy work until regulators publish guidance.", "延後政策工作至監管指引發布。"),
      ("Create competing policy tracks per department.", "各部門建立競爭性政策軌道。"),
      ["vision-workshop", "governance", "team-charter"]),
    S("You are managing a smart-city traffic program with predictive sensor deployment and agile citizen-alert apps. Planners and developers prioritize different outcomes. What should you do to establish a common vision?",
      "您管理智慧城市交通計畫，感測器預測式部署、市民警示 App 敏捷開發。規劃師與開發者優先順序不同。如何建立共同願景？",
      "Lead a hybrid alignment workshop connecting infrastructure milestones to citizen-facing OKRs in an integrated team charter.",
      "主導混合對齊工作坊，將基礎設施里程碑連結市民 OKR，記錄於整合團隊章程。",
      ("Complete sensors first; define app vision after hardware is live.", "先完成感測器，硬體上線後再定 App 願景。"),
      ("Let the agile team define vision independently.", "讓敏捷團隊獨立定義願景。"),
      ("Adopt transportation's vision without app team input.", "採納交通局願景，無 App 團隊投入。"),
      ("Skip alignment and use separate charters per workstream.", "跳過對齊，各工作流獨立章程。"),
      ["hybrid-alignment", "smart-city", "team-charter"]),
    S("You are the PM for a global sales enablement platform. Regional VPs want localization while the CRO demands standardized global vision. Kickoff is next week. What should you do?",
      "您是全球銷售賦能平台 PM。區域副總要在地化，CRO 要求標準化全球願景。啟動在下週。您應怎麼做？",
      "Facilitate a vision workshop with regional and executive stakeholders to define global core capabilities, localization boundaries, and OKRs in a team charter.",
      "引導區域與高階利害關係人願景工作坊，定義全球核心能力、在地化邊界及 OKR，記錄於團隊章程。",
      ("Implement only the CRO's global vision.", "僅實施 CRO 全球願景。"),
      ("Allow each region separate platforms without a charter.", "各區獨立平台，無共用章程。"),
      ("Delay kickoff until all VPs submit written proposals.", "延後啟動至所有副總提交書面提案。"),
      ("Use vendor default configuration as the vision.", "以廠商預設配置為願景。"),
      ["vision-workshop", "global-program", "OKR"]),
    S("You are leading a cybersecurity uplift. The CISO emphasizes zero-trust while business units resist workflow changes. Technical work started without agreed objectives. What is the FIRST step?",
      "您領導資安強化。CISO 強調零信任，事業單位抗拒流程變更。技術工作已在無共識目標下啟動。第一步為何？",
      "Facilitate a vision workshop aligning security objectives with business continuity goals and publish a team charter with shared OKRs.",
      "引導願景工作坊，使資安與業務連續性目標對齊，發布含共用 OKR 的團隊章程。",
      ("Mandate zero-trust by executive order without workshops.", "以高階命令強制零信任，無工作坊。"),
      ("Continue implementation and address resistance during training.", "繼續實施，抗拒留待訓練處理。"),
      ("Postpone security work until all units sign identical forms.", "延後資安工作至各單位簽相同表。"),
      ("Delegate vision entirely to the CISO technical team.", "願景完全委派 CISO 技術團隊。"),
      ["vision-workshop", "cybersecurity", "team-charter"]),
    S("You are the PM for retail omnichannel transformation. Store, e-commerce, and supply chain leaders describe different future-state visions. The board expects alignment before phase-two funding. What should you do?",
      "您是零售全通路轉型 PM。門市、電商與供應鏈主管描述不同未來願景。董事會期望第二階段資金前完成對齊。您應怎麼做？",
      "Organize a cross-functional vision workshop to synthesize a unified omnichannel vision with OKRs and a board-approved team charter.",
      "組織跨職能願景工作坊，綜合統一全通路願景與 OKR，取得董事會核准的團隊章程。",
      ("Fund phase two immediately and resolve gaps during implementation.", "立即撥第二階段資金，差距實施時解決。"),
      ("Adopt e-commerce vision since digital revenue is highest.", "採納電商願景，因數位營收最高。"),
      ("Create three parallel programs without alignment.", "三個平行計畫，不嘗試對齊。"),
      ("Use supply chain vision because inventory is easiest to measure.", "採供應鏈願景，因庫存最易衡量。"),
      ["vision-workshop", "omnichannel", "OKR"]),
    S("You are managing a water-utility smart-meter deployment. Environmental advocates, billing, and field technicians disagree on whether conservation or revenue accuracy anchors the vision. What should you do FIRST?",
      "您管理智慧水表部署。環保、帳務與現場技師對願景應以節水或計費準確為核心分歧。您首先應做什麼？",
      "Facilitate a stakeholder vision workshop to balance conservation and billing objectives, define shared OKRs, and document outcomes in a team charter.",
      "引導利害關係人願景工作坊，平衡節水與計費目標、定義共用 OKR，記錄於團隊章程。",
      ("Prioritize billing accuracy for immediate revenue impact.", "優先計費準確以立即影響收入。"),
      ("Deploy meters first and workshop vision after pilot data.", "先部署水表，試點資料後再工作坊。"),
      ("Exclude environmental advocates to speed consensus.", "排除環保倡議者以加速共識。"),
      ("Defer to the utility commission without facilitation.", "無引導會議下延後給公用事業委員會。"),
      ["vision-workshop", "public-utility", "team-charter"]),
    S("You are the PM for a pharmaceutical R&D data platform. Scientists, regulatory affairs, and IT articulate different data-sharing visions. Duplicate databases are being built. What is the BEST approach?",
      "您是製藥研發資料平台 PM。科學家、法規與 IT 對資料共享願景各異。正重複建置資料庫。最佳做法為何？",
      "Conduct a vision workshop with cross-functional leads to define shared data governance principles, OKRs, and a team charter before further development.",
      "與跨職能負責人舉辦願景工作坊，定義共用資料治理原則、OKR 與團隊章程，再進一步開發。",
      ("Allow each function to build preferred databases and integrate later.", "各職能建偏好資料庫，日後整合。"),
      ("Adopt IT architecture vision because they control infrastructure budget.", "採 IT 架構願景，因其控基礎設施預算。"),
      ("Pause indefinitely until global regulatory guidance finalizes.", "無限期暫停至全球法規定案。"),
      ("Outsource vision to a cloud vendor reference architecture.", "願景外包雲端廠商參考架構。"),
      ["vision-workshop", "data-governance", "team-charter"]),
],
"PPL2": [
    S("You are the Scrum Master for a fintech squad. During sprint planning, a senior developer and product owner argue about fixing technical debt versus delivering a regulatory feature. Others withdraw. What should you do FIRST?",
      "您是金融科技小隊 Scrum Master。衝刺規劃中資深開發與 PO 爭論修技術債或交付法規功能。其他人已退出。您首先應做什麼？",
      "Facilitate a structured discussion using team working agreements, help both express underlying interests, and guide toward a collaborative sprint goal.",
      "依工作協議引導結構化討論，協助雙方表達根本利益，引導朝向協作式衝刺目標。",
      ("Decide for the product owner since they prioritize the backlog.", "支持 PO，因其排序待辦。"),
      ("Split the team so each pursues preferred work independently.", "拆組各自獨立工作。"),
      ("Cancel planning and escalate to the engineering director.", "取消規劃並升級工程總監。"),
      ("Ignore the conflict and proceed with original backlog order.", "忽略衝突，依原待辦順序繼續。"),
      ["conflict-resolution", "scrum", "working-agreements"]),
    S("You are the PM on a construction program. Two subcontractor leads compete in meetings, refusing to share crane schedules and causing delays. Which conflict approach should you use FIRST?",
      "您是營建 PM。兩分包商負責人競爭，拒分享吊車排程致延誤。您首先應採哪種衝突方式？",
      "Use collaborating to facilitate a joint scheduling session where both share constraints and co-develop a workable crane allocation plan.",
      "採協作引導聯合排程，雙方分享限制並共同制定吊車分配計畫。",
      ("Use forcing and assign crane times by contract value.", "強迫，依合約金額分配吊車時段。"),
      ("Use avoiding and wait for one subcontractor to withdraw.", "迴避，等一方退出。"),
      ("Use accommodating and accept the larger subcontractor's schedule.", "順應，接受較大分包商排程。"),
      ("Use compromising by splitting crane time equally regardless of need.", "妥協，不論需求平均分配時間。"),
      ["Thomas-Kilmann", "conflict-resolution", "collaborating"]),
    S("You are the PM for marketing automation rollout. A BA and CRM admin clash repeatedly over data field definitions. Both are competent. What is the MOST effective response?",
      "您是行銷自動化 PM。BA 與 CRM 管理員因欄位定義反覆衝突。兩人能力俱佳。最有效回應為何？",
      "Facilitate working agreements defining data governance rules, escalation paths, and decision criteria for field definitions.",
      "引導工作協議，定義資料治理規則、升級路徑與欄位決策準則。",
      ("Reassign one member to a different project.", "調一人至其他專案。"),
      ("Make all field decisions yourself.", "所有欄位決策由您做。"),
      ("Postpone CRM configuration until informal agreement.", "延後設定至非正式達成共識。"),
      ("Escalate both to HR for performance management.", "兩人升級人資績效管理。"),
      ["working-agreements", "conflict-resolution", "facilitation"]),
    S("You are the Scrum Master for a Tokyo–São Paulo distributed team. A designer and backend developer have avoided conflict for two sprints, leaving integration issues unresolved. What should you do?",
      "您是東京—聖保羅分散團隊 Scrum Master。設計師與後端開發兩衝刺迴避衝突，整合問題未解。您應怎麼做？",
      "Coach both toward collaboration, facilitate a focused session to resolve integration issues, and update working agreements to prevent avoidance.",
      "輔導雙方協作，引導聚焦會議解決整合，更新工作協議防再度迴避。",
      ("Accept avoidance since some stories still deliver.", "接受迴避，因仍交付部分故事。"),
      ("Force the developer to implement without discussion.", "強制開發無討論實作。"),
      ("Remove both from the sprint and reassign stories.", "兩人移出衝刺，故事改派。"),
      ("Skip sprint review to hide integration problems.", "跳過審查隱藏整合問題。"),
      ["conflict-resolution", "virtual-teams", "working-agreements"]),
    S("You are the PM on a compliance upgrade. QA insists on exhaustive testing while development pushes faster releases for audit deadlines. Tension rises in status meetings. What should you do FIRST?",
      "您是合規升級 PM。品保堅持完整測試，開發推更快發布趕稽核。狀態會緊張升溫。您首先應做什麼？",
      "Facilitate problem-solving where both define minimum compliance criteria, testing scope boundaries, and document agreements in updated working protocols.",
      "引導問題解決，定義最低合規準則、測試邊界，記錄於更新工作規程。",
      ("Side with QA and halt releases until full regression completes.", "支持品保，全面回歸完成前停發布。"),
      ("Side with development and reduce testing for the deadline.", "支持開發，縮減測試趕期限。"),
      ("Escalate to the audit firm to choose the approach.", "升級稽核公司選方式。"),
      ("Rotate QA and development leads off the project.", "輪調品保與開發負責人。"),
      ["conflict-resolution", "collaborating", "working-agreements"]),
    S("You are the Scrum Master for an insurance claims team. Two testers blame developers publicly in retrospectives, creating hostility. Velocity dropped. What is the BEST response?",
      "您是保險理賠團隊 Scrum Master。兩測試人員回顧公開指責開發，敵對氣氛。速度下降。最佳回應為何？",
      "Facilitate a working agreement on respectful feedback norms and use private coaching with interest-based dialogue on blaming behavior.",
      "引導尊重回饋規範工作協議，並以利益導向對話私下輔導指責行為。",
      ("Remove testers from retrospectives.", "測試排除於回顧。"),
      ("Publicly reprimand testers at sprint review.", "衝刺審查公開訓斥測試。"),
      ("Ignore behavior hoping deadlines resolve it.", "忽略，期待期限化解。"),
      ("Report both to HR for immediate discipline.", "立即向人資檢舉要求處分。"),
      ["conflict-resolution", "scrum", "team-norms"]),
    S("You are the PM for warehouse automation. Operations and the integrator disagree on conveyor speed—a compromise failed. What should you do NEXT?",
      "您是倉儲自動化 PM。營運與整合商對輸送帶速度分歧，妥協失敗。下一步為何？",
      "Facilitate collaboration using operational data and safety requirements to co-design settings meeting throughput and safety objectives.",
      "引導協作，運用營運數據與安全需求共同設計滿足產量與安全目標。",
      ("Impose integrator settings since they hold the contract.", "強制整合商設定，因其有合約。"),
      ("Accept operations settings without analysis.", "無分析接受營運設定。"),
      ("Postpone commissioning until objections stop.", "延後試運轉至無異議。"),
      ("Split warehouse zones with conflicting settings.", "分區各用衝突設定。"),
      ["Thomas-Kilmann", "collaborating", "conflict-resolution"]),
    S("You are the Scrum Master for healthcare analytics. The PO and data engineer compete in every refinement, dismissing estimates. The team asked for help. What should you do FIRST?",
      "您是醫療分析 Scrum Master。PO 與資料工程師每次精煉競爭，互否估算。團隊求助。您首先應做什麼？",
      "Facilitate a working agreement on estimation practices and coach both to use collaborating during refinement.",
      "引導估算工作協議，輔導雙方精煉時採協作。",
      ("Ban the engineer from refinement.", "禁止工程師參加精煉。"),
      ("Let the PO override all estimates.", "PO 覆寫所有估算。"),
      ("Cancel refinement until conflict training completes.", "取消精煉至完成衝突訓練。"),
      ("Switch to predictive planning.", "改預測式規劃。"),
      ["Thomas-Kilmann", "scrum", "working-agreements"]),
    S("You are the PM for airport baggage-system upgrade. Facilities and vendor alternate forcing and accommodating, slipping milestones. What is the BEST intervention?",
      "您是機場行李系統 PM。設施與廠商交替強迫與順應，里程碑滑落。最佳介入為何？",
      "Facilitate structured conflict resolution using interest-based negotiation and update working agreements with clear decision rights.",
      "引導結構化衝突解決，利益導向協商，以明確決策權更新工作協議。",
      ("Terminate the vendor contract immediately.", "立即終止廠商合約。"),
      ("Let facilities make all remaining decisions.", "設施單方面做所有決策。"),
      ("Avoid conflict and focus only on schedule recovery.", "迴避衝突，只追回時程。"),
      ("Assign an auditor for every disputed decision.", "指派稽核員做所有爭議決策。"),
      ["conflict-resolution", "working-agreements", "negotiation"]),
    S("You are the Scrum Master for a gaming studio. Artists and programmers argue about scope creep. The PO adds mid-sprint items, fueling conflict. What should you do?",
      "您是遊戲工作室 Scrum Master。美術與程式爭論範疇蔓延，PO 衝刺中期加項。您應怎麼做？",
      "Facilitate working agreements on sprint change control and coach the PO and team on collaborative scope negotiation at refinement.",
      "引導衝刺變更控制工作協議，輔導 PO 與團隊精煉時協商範疇。",
      ("Support all mid-sprint PO additions.", "支持所有 PO 中期新增。"),
      ("Lock backlog and reject PO input until sprint end.", "鎖定待辦，衝刺結束前拒 PO。"),
      ("Split artists and programmers into separate teams.", "美術與程式拆成獨立團隊。"),
      ("Eliminate sprint commitments for continuous flow.", "取消衝刺承諾改持續流。"),
      ["scrum", "working-agreements", "conflict-resolution"]),
    S("You are the PM on data-center relocation. Network and facilities avoid rack-placement conflicts, causing last-minute migration changes. What prevents recurrence?",
      "您是資料中心遷移 PM。網路與設施迴避機架位置衝突，遷移週末臨時變更。如何防止 recurrence？",
      "Establish working agreements with mandatory collaborative planning and decision criteria for shared infrastructure before migration windows.",
      "建立工作協議，遷移窗口前強制協作規劃，為共用基礎設施定決策準則。",
      ("Assign rack placement exclusively to facilities.", "機架決策全由設施負責。"),
      ("Avoid pre-migration discussions to save time.", "迴避遷移前討論省時間。"),
      ("Use forcing during migration without prior collaboration.", "遷移週末強迫，事前不協作。"),
      ("Outsource rack decisions to the moving vendor.", "機架決策外包搬遷廠商。"),
      ["working-agreements", "conflict-resolution", "collaborating"]),
    S("You are the Scrum Master for e-commerce. Two developers block merges in code reviews due to rivalry. The charter lacks review norms. What should you do FIRST?",
      "您是電商 Scrum Master。兩開發因競爭在 code review 阻擋合併。章程缺審查規範。您首先應做什麼？",
      "Facilitate updated working agreements on code review norms, timelines, and collaborative conflict resolution, then coach both developers.",
      "引導更新 code review 規範、時限與協作衝突解決的工作協議，並輔導兩人。",
      ("Disable code reviews temporarily.", "暫停 code review。"),
      ("Remove one developer without addressing conflict.", "移一人，不處理衝突。"),
      ("Escalate both for disciplinary hearings.", "兩人升級紀律聽證。"),
      ("Allow rivalry since competition improves quality.", "允許競爭，因可提升品質。"),
      ["working-agreements", "scrum", "conflict-resolution"]),
    S("You are the PM for an energy joint venture. Parent-company PMs compete in steering meetings, confusing contractors. What is the MOST appropriate action?",
      "您是能源合資 PM。各母公司 PM 在指導會議競爭，承包商困惑。最適當行動為何？",
      "Facilitate a joint working agreement defining decision authority, meeting protocols, and collaborating for inter-company disputes.",
      "引導聯合工作協議，定義決策權、會議規程及跨公司爭議協作方式。",
      ("Let the larger parent's PM decide everything.", "較大母公司 PM 全決。"),
      ("Alternate decision authority weekly.", "每週輪替決策權。"),
      ("Avoid joint meetings; communicate separately.", "避免聯合會議，分別溝通。"),
      ("Replace both with an external PM.", "聘外部 PM 替換兩人。"),
      ["working-agreements", "joint-venture", "conflict-resolution"]),
    S("You are the Scrum Master for biotech research platform. A scientist and DevOps engineer clash over deployment windows in sprint planning. What should you do?",
      "您是生技研究平台 Scrum Master。科學家與 DevOps 衝刺規劃對部署窗口衝突。您應怎麼做？",
      "Facilitate working agreements defining deployment criteria, emergency exceptions, and collaborative window adjustment during planning.",
      "引導工作協議，定義部署準則、緊急例外及規劃中協作調整窗口。",
      ("Enforce fixed windows without exceptions.", "強制固定窗口無例外。"),
      ("Allow continuous uncontrolled releases.", "允許不受控持續發布。"),
      ("Remove the scientist from planning.", "科學家排除於規劃。"),
      ("Escalate to CTO for corporate deployment policy.", "升級 CTO 強加全公司政策。"),
      ["working-agreements", "scrum", "conflict-resolution"]),
    S("You are the PM for hotel rebranding. Agency and internal marketing accommodate silently, then complain after approval. What should you do?",
      "您是酒店 rebranding PM。Agency 與內部行銷默默順應，核准後才抱怨。您應怎麼做？",
      "Facilitate working agreements encouraging assertive collaborative feedback during design reviews rather than post-approval complaints.",
      "引導工作協議，鼓勵設計審查中斷言式協作回饋，而非核准後抱怨。",
      ("Replace the agency for accommodating too readily.", "替換過度順應的 agency。"),
      ("Accept post-approval complaints as normal rework.", "接受核准後抱怨為正常返工。"),
      ("Eliminate internal review to speed timeline.", "取消內部審查加速。"),
      ("Force-approve all agency designs without input.", "無內部投入強迫核准 agency 設計。"),
      ["Thomas-Kilmann", "working-agreements", "conflict-resolution"]),
],
}

# Add PPL3-PPL8 with similar structure - using abbreviated generation for remaining tasks
# I'll load from extended data inline

def load_extended_scenarios():
    """Load PPL3-PPL8 scenario banks."""
    ext = {}
    
    # PPL3 - Leadership
    ext["PPL3"] = [
        S("You are the PM leading a global ERP implementation. Workstream leads miss steering updates and bypass coordination by emailing executives directly. Compliant leads' morale is declining. Which leadership action BEST addresses this?",
          "您領導全球 ERP。工作流負責人缺席指導更新，繞過協調直接電郵高階主管。遵守者士氣下降。哪項領導行動最能處理？",
          "Reinforce the communication protocol in a team meeting, clarify escalation paths, and coach noncompliant leads on integrated reporting roles.",
          "團隊會議重申溝通協議、釐清升級路徑，並輔導未遵守者在整合報告中的角色。",
          ("Remove noncompliant leads before the next steering session.", "下次指導會前替換未遵守者。"),
          ("Stop steering meetings until all sign compliance agreements.", "暫停指導會至所有人簽合規協議。"),
          ("Allow direct emails so sponsors get faster updates.", "允許直接電郵讓發起人更快取得更新。"),
          ("Publicly reprimand noncompliant leads in the steering meeting.", "指導會公開訓斥未遵守者。"),
          ["team-leadership", "communication-protocol", "coaching"]),
        S("You are the PM of a fully virtual product team across five time zones. New members feel excluded from informal decision-making on chat channels. Engagement scores are falling. What should you do FIRST as a servant leader?",
          "您是跨五時區全虛擬產品團隊 PM。新成員感到被非正式聊天決策排除。參與度下降。僕僕領導下您首先應做什麼？",
          "Establish inclusive communication norms, rotate meeting times fairly, and create structured forums where all voices are heard before decisions.",
          "建立包容溝通規範、公平輪替會議時間，並建立決策前所有人發言的結構化論壇。",
          ("Mandate all decisions occur only in the headquarters time zone.", "規定所有決策僅在總部時區進行。"),
          ("Reduce ceremony frequency to minimize time-zone burden.", "減少儀式頻率以降低時區負擔。"),
          ("Allow informal chat decisions to preserve team autonomy.", "允許非正式聊天決策保留自主。"),
          ("Replace virtual members with co-located staff.", "以同地員工替換虛擬成員。"),
          ["servant-leadership", "virtual-teams", "inclusion"]),
        S("You are the PM for a critical infrastructure upgrade. A senior engineer shows signs of burnout but refuses time off before go-live. What demonstrates emotional intelligence?",
          "您是關鍵基礎設施升級 PM。資深工程師有倦怠跡象但拒絕 go-live 前休假。哪項展現情緒智慧？",
          "Have a private conversation acknowledging their dedication, assess workload distribution, and collaboratively plan relief coverage before go-live.",
          "私下認可其投入，評估工作分配，並協作規劃 go-live 前 relief 覆蓋。",
          ("Insist they take mandatory leave regardless of project needs.", "不論專案需求強制休假。"),
          ("Ignore burnout signs since go-live cannot slip.", "忽略倦怠，因 go-live 不能延。"),
          ("Reassign all their tasks immediately without discussion.", "無討論立即改派所有任務。"),
          ("Escalate their refusal to HR as insubordination.", "將拒絕升級人資視為不服从。"),
          ["emotional-intelligence", "team-care", "delegation"]),
        S("You are the PM on a regulatory reporting program. You micromanage analysts' daily tasks, and quality has not improved. What leadership adjustment should you make?",
          "您是監管報告 PM。您微觀管理分析師日常，品質未改善。應做何領導調整？",
          "Delegate outcomes with clear acceptance criteria, provide coaching on compliance standards, and establish checkpoints rather than task-level control.",
          "以明確驗收準則委派成果，輔導合規標準，建立檢查點而非任務級控制。",
          ("Increase daily task reviews to twice per day.", "每日任務審查增至兩次。"),
          ("Remove delegation entirely and complete analyses yourself.", "完全取消委派，自行完成分析。"),
          ("Rotate analysts weekly to prevent complacency.", "每週輪調分析師防懈怠。"),
          ("Outsource all analysis to eliminate management burden.", "外包所有分析消除管理負擔。"),
          ["delegation", "servant-leadership", "coaching"]),
        S("You are the release train engineer for fifteen agile teams. Team leads compete for your attention while struggling teams receive minimal support. What servant leadership action is MOST appropriate?",
          "您是十五個敏捷團隊的 RTE。負責人競爭您的關注， struggling 團隊支援不足。最適僕僕領導行動為何？",
          "Assess team health systematically, prioritize coaching for struggling teams, and establish office hours so support allocation is transparent and fair.",
          "系統評估團隊健康，優先輔導 struggling 團隊，建立 office hours 使支援分配透明公平。",
          ("Support only the highest-performing teams to maximize program outcomes.", "僅支援最高績效團隊以最大化成果。"),
          ("Rotate your attention equally regardless of team need.", "不論需求平等輪替關注。"),
          ("Delegate all coaching to product owners.", "所有輔導委派 PO。"),
          ("Eliminate one-on-one coaching to save time.", "取消一對一輔導省時間。"),
          ["servant-leadership", "SAFe", "coaching"]),
        S("You are the PM leading a hybrid program. Cross-functional leads have strong technical skills but avoid cross-workstream decisions, causing integration defects. Which TWO leadership actions should you take? (This will be used for multi-select variant)",
          "您領導混合計畫。跨職能負責人技術強但迴避跨工作流決策，致整合缺陷。",
          "Establish an integration cadence with decision logs linking gate milestones to sprint dependencies.",
          "建立整合節奏與決策紀錄，連結關卡里程碑與衝刺依賴。",
          ("Merge all squads into one predictive structure.", "合併為單一預測式結構。"),
          ("Reduce leadership visibility for self-resolution.", "降低領導能見度自行解決。"),
          ("Reward individual velocity over integration outcomes.", "以個別速度而非整合成果獎酬。"),
          ("Clarify decision rights in hybrid governance and hold leads accountable for cross-team commitments.", "混合治理中釐清決策權，使負責人對跨團隊承諾負責。"),
          ["servant-leadership", "hybrid-governance", "integration"]),
    ]
    
    # Generate more PPL3 scenarios programmatically
    ppl3_templates = [
        ("virtual team", "虛擬團隊", "servant-leadership", "Establish team agreements on core overlap hours, async documentation standards, and rotating facilitation to ensure equitable participation.", "建立核心重疊時段、非同步文件標準與輪替引導的團隊協議以確保公平參與。"),
        ("matrix organization", "矩陣組織", "delegation", "Clarify decision rights with functional and project managers, delegate work packages with explicit authority boundaries, and coach leads on navigating dual reporting.", "與職能及專案經理釐清決策權，以明確權限邊界委派工作包，並輔導負責人應對雙重匯報。"),
        ("crisis response", "危機應對", "emotional-intelligence", "Acknowledge team stress, provide clear priorities, remove non-critical tasks temporarily, and maintain visible presence without micromanaging execution.", "認可團隊壓力、提供清晰優先順序、暫移非關鍵任務，並保持能見度而不微觀管理執行。"),
        ("new team formation", "新團隊組成", "servant-leadership", "Facilitate team charter development covering values, decision norms, and psychological safety practices before assigning delivery work.", "指派交付工作前引導團隊章程，涵蓋價值觀、決策規範與心理安全實務。"),
        ("underperforming lead", "績效不佳負責人", "coaching", "Meet privately to understand barriers, co-create a performance improvement plan with measurable milestones, and provide targeted mentoring resources.", "私下了解障礙，共同制定含可衡量里程碑的績效改善計畫，並提供針對性導師資源。"),
        ("high-performing team", "高績效團隊", "delegation", "Delegate greater decision authority within guardrails, focus on removing organizational impediments, and avoid unnecessary intervention in team self-organization.", "在護欄內委派更大決策權，專注移除組織障礙，避免不必要介入團隊自組織。"),
        ("cultural diversity", "文化多元", "emotional-intelligence", "Provide cross-cultural communication training, adapt facilitation styles, and ensure meeting formats accommodate different participation preferences.", "提供跨文化溝通訓練、調整引導風格，確保會議形式適應不同參與偏好。"),
        ("remote onboarding", "遠端 onboarding", "virtual-teams", "Assign onboarding buddies across time zones, schedule structured pairing sessions, and maintain a team wiki with norms and contacts.", "跨時區指派 onboarding 夥伴，安排結構化配對會議，並維護含規範與聯絡人的團隊 wiki。"),
        ("executive pressure", "高階壓力", "servant-leadership", "Shield the team from reactive scope changes where possible, translate executive concerns into prioritized backlog items, and communicate trade-offs transparently.", "盡可能保護團隊免於 reactive 範疇變更，將高階疑慮轉為優先待辦，透明溝通權衡。"),
        ("skill gap", "技能缺口", "coaching", "Identify skill gaps through assessment, arrange targeted training or pairing, and delegate stretch assignments with supported learning plans.", "透過評估識別技能缺口，安排針對訓練或配對，並以支援學習計畫委派 stretch 任務。"),
    ]
    for ctx_en, ctx_zh, tag, ans_en, ans_zh in ppl3_templates:
        ext["PPL3"].append(S(
            f"You are the PM leading a {ctx_en} initiative. Team members look to you for direction but also need autonomy to deliver. Morale is mixed and delivery pressure is high. What leadership approach is MOST effective?",
            f"您領導{ctx_zh}計畫。成員既需方向也需自主交付。士氣不一且交付壓力高。最有效的領導方式為何？",
            ans_en, ans_zh,
            ("Take centralized control of all decisions to ensure consistency.", "集中控制所有決策以確保一致。"),
            ("Step back entirely and let the team self-organize without guidance.", "完全退讓，團隊無指引自組織。"),
            ("Focus only on reporting to executives and ignore team dynamics.", "僅專注向高階報告，忽略團隊動態。"),
            ("Replace underperforming members immediately to restore velocity.", "立即替換績效不佳者以恢復速度。"),
            [tag, "team-leadership", "coaching"]))
    
    # PPL4 - Stakeholder engagement
    ppl4_base = [
        S("You are the product owner for a loyalty platform. Marketing, legal, and support were engaged late and request mid-sprint changes. Velocity is stable. What improves engagement without destabilizing the iteration?",
          "您是忠誠度平台 PO。行銷、法務、客服較晚參與，要求衝刺中期變更。速度穩定。如何提升參與而不動搖迭代？",
          "Invite key stakeholders to sprint review and backlog refinement, capture requests in the backlog, and clarify how feedback enters future sprints.",
          "邀請關鍵利害關係人參加審查與精煉，需求納入待辦，說明回饋如何進入後續衝刺。",
          ("Accept all changes immediately and replan the sprint.", "立即接受所有變更並重規劃衝刺。"),
          ("Exclude late stakeholders until agile training completes.", "排除晚加入者至完成敏捷訓練。"),
          ("Send weekly email summaries and avoid live sessions.", "僅每週電郵摘要，避免現場會議。"),
          ("Freeze the backlog permanently to prevent disruption.", "永久凍結待辦以防干擾。"),
          ["stakeholder-engagement", "sprint-review", "backlog-refinement"]),
        S("You are the PM for a pharmaceutical packaging upgrade. Operators were consulted after layouts were finalized. Consultant engagement is strong but operator resistance delays trials. What improves engagement?",
          "您是藥品包裝升級 PM。布局定案後才徵詢操作員。顧問參與強但操作員抗拒延遲試運轉。如何改善參與？",
          "Conduct structured walkthroughs with operators on proposed layouts and capture usability impacts in the requirements trace matrix.",
          "與操作員就提案布局結構化走查，將可用性影響納入需求追溯矩陣。",
          ("Limit operators to post-validation sign-off only.", "操作員僅限驗證後簽核。"),
          ("Route all operator concerns through consultants.", "所有操作員疑慮改由顧問處理。"),
          ("Replace operator reps with managers mid-project.", "中期以主管替換操作員代表。"),
          ("Proceed with trials despite resistance to maintain schedule.", "儘管抗拒仍進行試運轉以保時程。"),
          ["stakeholder-engagement", "operator-involvement", "requirements"]),
    ]
    ppl4_templates = [
        ("power/interest grid", "權力/利益方格", "Update the stakeholder engagement plan using power/interest analysis to tailor communication frequency and involvement level per group.", "運用權力/利益分析更新利害關係人參與計畫，依群組調整溝通頻率與參與程度。"),
        ("salience model", "顯著性模型", "Reassess stakeholders using the salience model and adjust engagement strategies for those with high power, urgency, or legitimacy.", "以顯著性模型重評利害關係人，調整高權力、緊迫或合法性者的參與策略。"),
        ("sprint review", "衝刺審查", "Invite skeptical stakeholders to sprint reviews with demo-ready increments to build trust through tangible progress.", "邀請持疑利害關係人參加含可演示增量的衝刺審查，以具體進度建立信任。"),
        ("engagement assessment", "參與評估", "Perform engagement assessment mapping current versus desired levels and define targeted actions to move resistant stakeholders toward supportive.", "執行參與評估，對照現況與期望程度，定義行動使抗拒者轉向支持。"),
        ("community rollout", "社區推廣", "Establish community liaison sessions and feedback loops before major rollout milestones to surface concerns early.", "重大推廣里程碑前建立社區聯絡會議與回饋迴路，及早浮現疑慮。"),
        ("vendor ecosystem", "廠商生態", "Facilitate a stakeholder mapping session including vendors and partners, then define engagement roles in the stakeholder register.", "引導含廠商與夥伴的利害關係人對應會議，並於登錄表定義參與角色。"),
        ("executive sponsor", "高階發起人", "Align with the executive sponsor on key messages and co-present at milestone reviews to reinforce commitment visibly.", "與高階發起人對齊關鍵訊息，於里程碑審查共同簡報以可見方式強化承諾。"),
        ("regulatory body", "監管機構", "Schedule structured briefings with regulatory stakeholders aligned to gate milestones and document concerns in the issue log.", "依關卡里程碑安排與監管利害關係人的結構化簡報，疑慮記錄於議題日誌。"),
        ("internal resistance", "內部抗拒", "Identify root causes through one-on-one listening sessions and co-create mitigation actions documented in the engagement plan.", "透過一對一聆聽識別根本原因，共同制定記錄於參與計畫的減緩行動。"),
        ("customer advisory", "客戶諮詢", "Form a customer advisory group with defined cadence and feed validated input into backlog refinement ceremonies.", "組成具固定頻率的客戶諮詢小組，將驗證後投入納入待辦精煉儀式。"),
        ("union stakeholders", "工會利害關係人", "Engage union representatives early in change impact assessments and include them in working group sessions.", "於變更影響評估早期讓工會代表參與，並納入工作小組會議。"),
        ("silent stakeholders", "沉默利害關係人", "Proactively reach out to unengaged stakeholders identified in the register and schedule targeted interviews to understand barriers.", "主動聯繫登錄表中未參與者，安排針對性訪談了解障礙。"),
        ("conflicting priorities", "衝突優先順序", "Facilitate a prioritization workshop with competing stakeholders using agreed criteria and document decisions in the charter.", "以共識準則引導競爭利害關係人優先順序工作坊，決策記錄於章程。"),
    ]
    ext["PPL4"] = list(ppl4_base)
    for method_en, method_zh, ans_en, ans_zh in ppl4_templates:
        ext["PPL4"].append(S(
            f"You are the PM for an enterprise transformation. Several influential stakeholders show neutral or resistant engagement levels despite repeated status emails. You need to improve participation before the next major milestone. What should you do?",
            f"您負責企業轉型。儘管多次狀態電郵，數位具影響力利害關係人仍中性或抗拒。下一重大里程碑前需提升參與。您應怎麼做？",
            ans_en, ans_zh,
            ("Increase email frequency to daily status broadcasts.", "將狀態電郵增至每日廣播。"),
            ("Exclude resistant stakeholders from decisions to speed progress.", "排除抗拒者於決策外以加速。"),
            ("Wait until go-live when benefits become visible.", "等待上線後效益可見再說。"),
            ("Escalate all resistant stakeholders to the sponsor for replacement.", "所有抗拒者升級發起人要求替換。"),
            ["stakeholder-engagement", "engagement-matrix", method_en.replace("/", "-").replace(" ", "-")]))
    
    # PPL5 - Support team performance
    ppl5_templates = [
        ("forecast maturity", "預測成熟度", "Assess forecast maturity across teams, provide rolling-wave planning training, and establish baseline metrics before holding teams to unified reporting standards.", "評估各團隊預測成熟度，提供滾動式規劃訓練，在統一報告標準前先建立基準指標。"),
        ("multi-department baseline", "多部門基準", "Facilitate cross-department workshops to align on shared baseline assumptions, resource calendars, and interdependency milestones.", "引導跨部門工作坊，對齊共用基準假設、資源日曆與相互依賴里程碑。"),
        ("expectation alignment", "期望對齊", "Conduct expectation alignment sessions with functional managers on capacity, priority trade-offs, and definition of done for shared deliverables.", "與職能經理舉行期望對齊會議，就產能、優先權衡與共用交付物完成定義達成共識。"),
        ("performance metrics", "績效指標", "Define balanced team performance metrics combining delivery, quality, and collaboration indicators rather than velocity alone.", "定義平衡的团队績效指標，結合交付、品質與協作，而非僅速度。"),
        ("resource leveling", "資源平衡", "Analyze resource conflicts across departments, negotiate shared priorities with sponsors, and update the resource management plan.", "分析跨部門資源衝突，與發起人協商共用優先順序，更新資源管理計畫。"),
        ("skill development", "技能發展", "Create a team development plan linking skill gaps to training, mentoring, and stretch assignments with measurable outcomes.", "建立團隊發展計畫，將技能缺口連結訓練、導師與含可衡量成果的 stretch 任務。"),
        ("OKR alignment", "OKR 對齊", "Map team OKRs to program objectives in a collaborative session and review alignment at each quarterly planning increment.", "協作會議中將團隊 OKR 對應計畫目標，並於每季規劃增量審查對齊。"),
        ("distributed accountability", "分散問責", "Clarify RACI across departments for shared deliverables and review accountability in integrated status forums.", "為共用交付物跨部門釐清 RACI，並於整合狀態論壇審查問責。"),
    ]
    ext["PPL5"] = []
    for topic_en, topic_zh, ans_en, ans_zh in ppl5_templates:
        for variant in range(2):
            ext["PPL5"].append(S(
                f"You are the PM overseeing a {topic_en.replace('_', ' ')} challenge across multiple departments. Teams report progress differently and executives question comparability. What should you do FIRST?",
                f"您監督跨多部門的{topic_zh}挑戰。團隊以不同方式報告進度，高階質疑可比性。您首先應做什麼？",
                ans_en, ans_zh,
                ("Mandate a single reporting template without stakeholder workshops.", "無工作坊強制單一報告範本。"),
                ("Rank departments publicly by velocity to drive competition.", "公開依速度排名部門以驅動競爭。"),
                ("Delay executive reporting until all teams match best performer metrics.", "延後高階報告至所有團隊達最佳者指標。"),
                ("Outsource performance management to HR without PM involvement.", "績效管理外包人資，PM 不介入。"),
                ["team-performance", topic_en.replace(" ", "-"), "expectation-alignment"]))
    
    # PPL6 - Manage expectations
    ppl6_templates = [
        ("roadmap", "路線圖", "Publish a transparent roadmap with confidence levels, assumptions, and review cadence agreed with stakeholders.", "發布含信心水準、假設與利害關係人共識審查頻率的透明路線圖。"),
        ("pilot lessons", "試點教訓", "Conduct a pilot retrospective with executives and operators, document lessons learned, and adjust forecast and scope messaging before scaling.", "與高階及操作員舉行試點回顧，記錄教訓，擴展前調整預測與範疇溝通。"),
        ("executive updates", "高階更新", "Deliver executive updates using earned value and milestone trends with explicit risk and assumption sections rather than optimistic narratives.", "高階更新使用實獲值與里程碑趨勢，含明確風險與假設章節，而非樂觀敘述。"),
        ("scope communication", "範疇溝通", "Facilitate an expectation reset session when scope changes, documenting what is in/out and impacts on dates and resources.", "範疇變更時引導期望重設會議，記錄納入/排除項目及對日期與資源影響。"),
        ("benefit timeline", "效益時程", "Align stakeholders on benefit realization timelines separate from delivery milestones to prevent false completion assumptions.", "使利害關係人對效益實現時程與交付里程碑分開對齊，避免錯誤完成假設。"),
        ("change impact", "變更影響", "Use structured change impact communications with before/after comparisons and explicit decision deadlines for stakeholders.", "以結構化變更影響溝通，含前後對照及明確決策截止日。"),
    ]
    ext["PPL6"] = []
    for topic_en, topic_zh, ans_en, ans_zh in ppl6_templates:
        for variant in range(3):
            ext["PPL6"].append(S(
                f"You are the PM for a complex program. Stakeholders express frustration that prior {topic_en.replace('_', ' ')} communications created unrealistic expectations about go-live readiness. What should you do?",
                f"您負責複雜計畫。利害關係人抱怨先前{topic_zh}溝通造成對 go-live 準備度的不實期望。您應怎麼做？",
                ans_en, ans_zh,
                ("Promise an accelerated timeline to restore stakeholder confidence.", "承諾加速時程以恢復信心。"),
                ("Reduce communication frequency to avoid further disappointment.", "減少溝通頻率以免再度失望。"),
                ("Blame the previous PM and continue existing messaging.", "归咎前任 PM 並延續現有訊息。"),
                ("Share only positive metrics in the next executive briefing.", "下次高階簡報僅分享正面指標。"),
                ["manage-expectations", topic_en.replace(" ", "-"), "stakeholder-communication"]))
    
    # PPL7 - Knowledge transfer
    ppl7_templates = [
        ("pair programming", "配對程式設計", "Institute pair programming rotations for critical modules and document design decisions in the team wiki during pairing sessions.", "關鍵模組實施配對程式輪替，配對期間於團隊 wiki 記錄設計決策。"),
        ("wiki/runbooks", "wiki/Runbook", "Maintain updated runbooks and wiki pages with troubleshooting steps, ownership, and links to decision logs for operational handoffs.", "維護含故障排除步驟、負責人與決策紀錄連結的 runbook 與 wiki，供營運交接。"),
        ("lessons learned", "教訓學習", "Facilitate structured lessons learned sessions at phase gates and sprint retrospectives, storing outcomes in a searchable repository.", "於階段關卡與衝刺回顧引導結構化教訓學習，成果存入可搜尋儲庫。"),
        ("knowledge transfer", "知識移轉", "Create a knowledge transfer plan with shadowing schedules, competency checklists, and sign-off criteria before key resources depart.", "關鍵資源離開前制定含 shadowing 排程、能力檢核表與簽核準則的知識移轉計畫。"),
        ("communities of practice", "實務社群", "Establish a community of practice with regular knowledge-sharing sessions and curated repositories for reusable assets.", "建立實務社群，定期知識分享並策展可重用資產儲庫。"),
        ("documentation debt", "文件債", "Allocate sprint capacity for documentation debt reduction with acceptance criteria tied to operational readiness reviews.", "分配衝刺產能處理文件債，驗收準則連結營運準備審查。"),
        ("cross-training", "交叉訓練", "Implement cross-training matrices identifying backup owners for each critical skill and track completion in team performance reviews.", "實施交叉訓練矩陣，為各關鍵技能指定備援負責人，並於績效審查追蹤完成度。"),
    ]
    ext["PPL7"] = []
    for topic_en, topic_zh, ans_en, ans_zh in ppl7_templates:
        for variant in range(3):
            ext["PPL7"].append(S(
                f"You are the PM preparing for operational handoff. The team relies on tacit knowledge and {topic_en.replace('_', ' ')} practices are inconsistent. Support teams fear they cannot sustain the solution. What should you do FIRST?",
                f"您準備營運交接。團隊依賴默會知識，{topic_zh}實務不一致。支援團隊擔心無法維持方案。您首先應做什麼？",
                ans_en, ans_zh,
                ("Delay handoff until the original development team agrees to stay indefinitely.", "延後交接至原開發團隊同意無限期留任。"),
                ("Transfer only executable code without documentation to save time.", "僅移交可執行程式碼，不寫文件以省時間。"),
                ("Record ad-hoc verbal briefings without structured repositories.", "以非結構化方式記錄臨時口頭簡報。"),
                ("Outsource sustainment entirely to avoid internal knowledge transfer.", "完全外包維運以避免內部知識移轉。"),
                ["knowledge-transfer", topic_en.replace(" ", "-"), "operational-readiness"]))
    
    # PPL8 - Communication
    ppl8_templates = [
        ("communication plan", "溝通計畫", "Update the communication plan with audience segmentation, message types, channels, frequency, and owner accountability for each stakeholder group.", "更新溝通計畫，含受眾分群、訊息類型、管道、頻率及各利害關係人群組的負責問責。"),
        ("RACI", "RACI", "Define RACI for project communications so authors, approvers, and distributors are clear, preventing duplicate or unauthorized messages.", "為專案溝通定義 RACI，釐清撰寫、核准與發布者，防止重複或未授權訊息。"),
        ("SAFe tiered communication", "SAFe 分層溝通", "Implement a tiered communication matrix aligning team ceremonies, program increment summaries, and executive digests with distinct content and cadence.", "實施分層溝通矩陣，對齊團隊儀式、PI 摘要與高階摘要的內容與頻率。"),
        ("audience segmentation", "受眾分群", "Segment audiences by information needs and tailor message detail—executives receive decision summaries while teams receive actionable specifics.", "依資訊需求分群受眾，調整訊息細節——高階收決策摘要，團隊收可執行細節。"),
        ("crisis communication", "危機溝通", "Activate the crisis communication plan with a single authorized spokesperson, predefined message templates, and regular update intervals.", "啟動危機溝通計畫，單一授權發言人、預定訊息範本與固定更新間隔。"),
        ("status reporting", "狀態報告", "Standardize status report templates across workstreams with consistent RAG definitions and escalation triggers documented in the communication plan.", "跨工作流標準化狀態報告範本，含一致 RAG 定義與升級觸發，記錄於溝通計畫。"),
        ("change communication", "變更溝通", "Coordinate change communications through a central calendar with approval workflows to prevent conflicting messages to the same audience.", "透過中央月曆協調變更溝通，含核准流程，防止對同一受眾發送衝突訊息。"),
    ]
    ext["PPL8"] = []
    for topic_en, topic_zh, ans_en, ans_zh in ppl8_templates:
        for variant in range(3):
            ext["PPL8"].append(S(
                f"You are the PM for a multi-workstream program. Stakeholders report confusion from overlapping updates and inconsistent {topic_en.replace('_', ' ')} practices. What should you do?",
                f"您負責多工作流計畫。利害關係人反映重疊更新與不一致的{topic_zh}實務造成混淆。您應怎麼做？",
                ans_en, ans_zh,
                ("Allow each workstream to communicate independently without coordination.", "各工作流獨立溝通，無需協調。"),
                ("Reduce all communication to verbal updates only.", "所有溝通改為僅口頭更新。"),
                ("Send identical detailed reports to all audiences regardless of role.", "不論角色向所有受眾發送相同詳盡報告。"),
                ("Eliminate written records to increase communication speed.", "取消書面紀錄以提高溝通速度。"),
                ["communication-plan", topic_en.replace(" ", "-"), "stakeholder-communication"]))
    
    return ext

EXT = load_extended_scenarios()
for k, v in EXT.items():
    SCENARIOS[k] = v

# Multi-select scenario variants - extra options for 5-option multi questions
MULTI_EXTRA = {
    "PPL1": ("Which TWO actions should you include in the team alignment approach? (Select two.)", "您應在團隊對齊方式納入哪兩項行動？（選兩項）"),
    "PPL2": ("Which TWO responses best address this conflict? (Select two.)", "哪兩項回應最能處理此衝突？（選兩項）"),
    "PPL3": ("Which TWO leadership actions should you take? (Select two.)", "您應採取哪兩項領導行動？（選兩項）"),
    "PPL4": ("Which TWO actions best improve stakeholder engagement? (Select two.)", "哪兩項行動最能改善利害關係人參與？（選兩項）"),
    "PPL5": ("Which TWO actions best support team performance? (Select two.)", "哪兩項行動最能支持團隊績效？（選兩項）"),
    "PPL6": ("Which TWO actions best manage stakeholder expectations? (Select two.)", "哪兩項行動最能管理利害關係人期望？（選兩項）"),
    "PPL7": ("Which TWO actions best ensure knowledge transfer? (Select two.)", "哪兩項行動最能確保知識移轉？（選兩項）"),
    "PPL8": ("Which TWO changes should you make to the communication approach? (Select two.)", "您應對溝通方式做哪兩項調整？（選兩項）"),
}

MULTI_SECOND_CORRECT = {
    "PPL1": ("Document shared OKRs and review them in recurring alignment checkpoints.", "記錄共用 OKR 並於定期對齊檢查點審查。"),
    "PPL2": ("Coach both parties privately to express interests before the next planning session.", "私下輔導雙方於下次規劃前表達利益訴求。"),
    "PPL3": ("Clarify decision rights in the governance model and hold leads accountable for cross-team commitments.", "於治理模型釐清決策權，使負責人對跨團隊承諾負責。"),
    "PPL4": ("Update the stakeholder engagement plan with influence strategies, meeting cadence, and feedback resolution owners.", "更新參與計畫，納入影響策略、會議頻率與回饋處理負責人。"),
    "PPL5": ("Establish cross-department baseline metrics and review them in integrated performance forums.", "建立跨部門基準指標，於整合績效論壇審查。"),
    "PPL6": ("Schedule structured expectation reset sessions when forecasts change, documenting impacts transparently.", "預測變更時安排結構化期望重設會議，透明記錄影響。"),
    "PPL7": ("Create shadowing schedules with competency checklists before key resources transition off the project.", "關鍵資源離開前建立含能力檢核表的 shadowing 排程。"),
    "PPL8": ("Publish a shared communication calendar showing message types, audiences, and approval deadlines.", "發布共用溝通月曆，標示訊息類型、受眾與核准截止日。"),
}

MULTI_DISTRACTORS = [
    ("Escalate immediately to the sponsor without attempting team-level resolution.", "立即升級發起人，不嘗試團隊層級解決。"),
    ("Remove the involved parties from the project to eliminate friction quickly.", "將相關人員移出專案以快速消除摩擦。"),
    ("Delay all decisions until the next phase gate regardless of impact.", "不論影響，所有決策延至下一階段關卡。"),
    ("Implement changes unilaterally without stakeholder consultation.", "未徵詢利害關係人即單方面實施變更。"),
    ("Eliminate formal communication channels to reduce overhead.", "取消正式溝通管道以降低開銷。"),
]

CORRECT_REASON_EN = "it addresses the root cause through collaborative, structured engagement aligned with PMI people-domain practices"
CORRECT_REASON_ZH = "其透過符合 PMI 人員領域實務的協作式結構化參與處理根本原因"

WRONG_REASONS_EN = [
    "it skips essential alignment or facilitation and risks embedding wrong priorities or unresolved conflict",
    "it imposes decisions without consensus, damaging trust and shared ownership",
    "it defers critical people work, allowing problems to persist and increase downstream impact",
    "it escalates prematurely or removes people before facilitation is attempted, which is disproportionate",
    "it avoids the issue rather than resolving it through structured dialogue and working agreements",
]
WRONG_REASONS_ZH = [
    "其跳過必要的對齊或引導，可能固化錯誤優先順序或未解決的衝突",
    "其在未達成共識下強加決策，損害信任與共同承擔",
    "其延後關鍵人員工作，使問題持續並增加下游影響",
    "其過早升級或在未嘗試引導前就移除人員，過於激烈",
    "其迴避問題而非透過結構化對話與工作協議解決",
]


def distribute(count, weights):
    """Distribute count items by weights proportionally."""
    total = sum(weights)
    raw = [count * w / total for w in weights]
    result = [int(r) for r in raw]
    remainder = count - sum(result)
    fractions = [(i, raw[i] - result[i]) for i in range(len(weights))]
    fractions.sort(key=lambda x: -x[1])
    for i in range(remainder):
        result[fractions[i][0]] += 1
    return result


def classify_wrong_reason(option_en):
    """Return reason index based on distractor content."""
    o = option_en.lower()
    if any(w in o for w in ["escalat", "remov", "replac", "terminat", "disciplin", "reprimand", "report"]):
        return 3
    if any(w in o for w in ["delay", "defer", "postpone", "wait", "skip", "ignore", "avoid"]):
        return 2
    if any(w in o for w in ["mandat", "forc", "impos", "decree", "unilateral", "override", "reject all"]):
        return 1
    if any(w in o for w in ["exclud", "ban", "eliminate", "allow each", "independently without"]):
        return 0
    if any(w in o for w in ["split", "separat", "compet", "rank", "publicly"]):
        return 4
    return 0


def build_explanation(correct_idx, options_en, options_zh, is_multi=False, correct_indices=None, qid=""):
    letters = "ABCDE"
    if is_multi:
        correct_set = set(correct_indices)
        parts_en = []
        parts_zh = []
        for i in range(len(options_en)):
            if i in correct_set:
                parts_en.append(f"Option {letters[i]} is correct because it supports effective people leadership through structured, collaborative action aligned with PMI practices.")
                parts_zh.append(f"選項 {letters[i]} 正確，因其透過符合 PMI 實務的結構化協作行動支持有效的人員領導。")
            else:
                r = classify_wrong_reason(options_en[i])
                parts_en.append(f"Option {letters[i]} is incorrect because {WRONG_REASONS_EN[r]}.")
                parts_zh.append(f"選項 {letters[i]} 錯誤，因為{WRONG_REASONS_ZH[r]}。")
        return " ".join(parts_en), " ".join(parts_zh)

    parts_en = [f"Option {letters[correct_idx]} is correct because {CORRECT_REASON_EN}."]
    parts_zh = [f"選項 {letters[correct_idx]} 正確，因為{CORRECT_REASON_ZH}。"]
    for i in range(4):
        if i != correct_idx:
            r = classify_wrong_reason(options_en[i])
            parts_en.append(f"Option {letters[i]} is incorrect because {WRONG_REASONS_EN[r]}.")
            parts_zh.append(f"選項 {letters[i]} 錯誤，因為{WRONG_REASONS_ZH[r]}。")
    return " ".join(parts_en), " ".join(parts_zh)


def make_mcq(qid, task, approach, difficulty, scenario, scenario_idx):
    stem_en, stem_zh, correct_en, correct_zh, distractors, tags = scenario
    options = [{"en": correct_en, "zh": correct_zh}]
    for d_en, d_zh in distractors:
        options.append({"en": d_en, "zh": d_zh})
    # Shuffle options deterministically per question id
    indices = list(range(4))
    rng = random.Random(qid)
    rng.shuffle(indices)
    shuffled = [options[i] for i in indices]
    correct = indices.index(0)
    exp_en, exp_zh = build_explanation(correct, [o["en"] for o in shuffled], [o["zh"] for o in shuffled], qid=qid)
    return {
        "id": qid,
        "type": "mcq",
        "domain": "people",
        "task": task,
        "approach": approach,
        "difficulty": difficulty,
        "stem": {"en": stem_en, "zh": stem_zh},
        "options": shuffled,
        "correct": correct,
        "explanation": {"en": exp_en, "zh": exp_zh},
        "tags": tags,
    }


def make_multi(qid, task, approach, difficulty, scenario, scenario_idx):
    stem_en, stem_zh, correct_en, correct_zh, distractors, tags = scenario
    suffix_en, suffix_zh = MULTI_EXTRA[task]
    second_en, second_zh = MULTI_SECOND_CORRECT[task]
    
    correct_opts = [
        {"en": correct_en, "zh": correct_zh},
        {"en": second_en, "zh": second_zh},
    ]
    wrong_opts = [{"en": d[0], "zh": d[1]} for d in distractors[:2]]
    extra_wrong = [{"en": d[0], "zh": d[1]} for d in MULTI_DISTRACTORS[scenario_idx % len(MULTI_DISTRACTORS):scenario_idx % len(MULTI_DISTRACTORS)+3]]
    while len(extra_wrong) < 3:
        d = MULTI_DISTRACTORS[len(extra_wrong) % len(MULTI_DISTRACTORS)]
        extra_wrong.append({"en": d[0], "zh": d[1]})
    
    all_opts = correct_opts + wrong_opts + extra_wrong[:3]
    all_opts = all_opts[:5]
    
    rng = random.Random(qid + "_multi")
    indices = list(range(len(all_opts)))
    rng.shuffle(indices)
    shuffled = [all_opts[i] for i in indices]
    correct_indices = sorted([indices.index(0), indices.index(1)])
    
    exp_en, exp_zh = build_explanation(0, [o["en"] for o in shuffled], [o["zh"] for o in shuffled],
                                         is_multi=True, correct_indices=correct_indices, qid=qid)
    return {
        "id": qid,
        "type": "multi",
        "domain": "people",
        "task": task,
        "approach": approach,
        "difficulty": difficulty,
        "stem": {"en": stem_en + " " + suffix_en, "zh": stem_zh + suffix_zh},
        "options": shuffled,
        "correct": correct_indices,
        "selectN": 2,
        "explanation": {"en": exp_en, "zh": exp_zh},
        "tags": tags,
    }


def assign_attributes(count):
    """Return list of (task, approach, difficulty, is_multi) tuples."""
    task_counts = distribute(count, [1]*8)
    approach_counts = distribute(count, APPROACH_WEIGHTS)
    diff_counts = distribute(count, DIFF_WEIGHTS)
    multi_count = round(count * 0.12)
    mcq_count = count - multi_count
    
    tasks = []
    for i, c in enumerate(task_counts):
        tasks.extend([TASKS[i]] * c)
    approaches = []
    for i, c in enumerate(approach_counts):
        approaches.extend([APPROACHES[i]] * c)
    diffs = []
    for i, c in enumerate(diff_counts):
        diffs.extend([DIFFICULTIES[i]] * c)
    types = [False]*mcq_count + [True]*multi_count
    
    rng = random.Random(42)
    combined = list(zip(tasks, approaches, diffs, types))
    rng.shuffle(combined)
    return combined


def generate_file(filename, start_num, end_num):
    count = end_num - start_num + 1
    attrs = assign_attributes(count)
    questions = []
    
    task_counters = {t: 0 for t in TASKS}
    
    for i, num in enumerate(range(start_num, end_num + 1)):
        qid = f"PPL-{num:04d}"
        task, approach, difficulty, is_multi = attrs[i]
        scenarios = SCENARIOS[task]
        idx = task_counters[task] % len(scenarios)
        task_counters[task] += 1
        scenario = scenarios[idx]
        
        if is_multi:
            q = make_multi(qid, task, approach, difficulty, scenario, idx)
        else:
            q = make_mcq(qid, task, approach, difficulty, scenario, idx)
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
        print(f"Wrote {n} questions to {path}")
        total += n
    print(f"Total: {total} questions")


if __name__ == "__main__":
    main()
