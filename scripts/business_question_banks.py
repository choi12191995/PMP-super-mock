"""Question content banks for PMP business domain generator."""

def opt(en, zh):
    return {"en": en, "zh": zh}

def q(stem_en, stem_zh, options, correct, expl_en, expl_zh, tags):
    return {
        "stem": {"en": stem_en, "zh": stem_zh},
        "options": options,
        "correct": correct,
        "explanation": {"en": expl_en, "zh": expl_zh},
        "tags": tags,
    }

INDUSTRIES = [
    ("healthcare", "醫療保健", "hospital network", "醫院體系"),
    ("fintech", "金融科技", "digital bank", "數位銀行"),
    ("manufacturing", "製造業", "smart factory", "智慧工廠"),
    ("telecom", "電信", "5G rollout", "5G 部署"),
    ("energy", "能源", "renewable grid", "再生能源電網"),
    ("retail", "零售", "omnichannel platform", "全通路平台"),
    ("government", "政府", "public services portal", "公共服務入口"),
    ("aerospace", "航太", "satellite program", "衛星計畫"),
    ("insurance", "保險", "claims modernization", "理賠現代化"),
    ("logistics", "物流", "warehouse automation", "倉儲自動化"),
    ("education", "教育", "learning management system", "學習管理系統"),
    ("construction", "營造", "infrastructure upgrade", "基礎設施升級"),
]

def _stems(t, ind):
    """Format bilingual stems: English uses EN industry/project names."""
    en = t[0].format(ind=ind[0], proj=ind[2], ind_zh=ind[1], proj_zh=ind[3])
    zh = t[1].format(ind=ind[1], proj=ind[3], ind_zh=ind[1], proj_zh=ind[3])
    return en, zh

def _stems_ind_only(t, ind):
    en = t[0].format(ind=ind[0], ind_zh=ind[1])
    zh = t[1].format(ind=ind[1], ind_zh=ind[1])
    return en, zh

VARIANTS = [
    (" The initiative spans multiple business units with competing priorities.", " 此計畫橫跨多個業務單位且優先順序相互競爭。"),
    (" Executive leadership has set aggressive quarterly milestones.", " 高階領導設定了積極的季度里程碑。"),
    (" Recent organizational restructuring has changed reporting lines.", " 近期組織重組已改變報告線。"),
    (" The project is funded through a strategic transformation budget.", " 專案由策略轉型預算資助。"),
    (" A recent internal audit highlighted gaps in this area.", " 近期內部稽核強調此領域的缺口。"),
    (" The contract includes strict SLA penalties for delays.", " 合約包含對延遲的嚴格 SLA 罰則。"),
    (" Cross-functional teams in three regions depend on your decision.", " 三個區域的跨職能團隊依賴你的決策。"),
    (" The sponsor expects a recommendation at tomorrow's review.", " 贊助者期望在明天的審查中獲得建議。"),
    (" Stakeholders have raised concerns in the last governance meeting.", " 利害關係人在上次治理會議中提出疑慮。"),
    (" The program is entering a critical phase next month.", " 計畫下月進入關鍵階段。"),
]

def _add_variant(stem_en, stem_zh, idx):
    v = VARIANTS[idx % len(VARIANTS)]
    return stem_en + v[0], stem_zh + v[1]

# Each entry: (stem_en, stem_zh, options, correct_index, expl_en, expl_zh, tags)
# Options are list of (en, zh) tuples

def _rotate(opts, correct, shift):
    n = len(opts)
    s = shift % n
    rotated = [opts[(i + s) % n] for i in range(n)]
    new_correct = (correct - s) % n
    return [opt(e, z) for e, z in rotated], new_correct

def get_be1_mcq(idx):
    templates = [
        ("You are leading a {proj} initiative. The enterprise PMO requires monthly portfolio KPI reporting while the steering committee wants faster local vendor dispute resolution without bypassing oversight. What should you implement first?",
         "你領導 {proj_zh} 計畫。企業 PMO 要求每月回報組合 KPI，指導委員會希望在供應商爭議上加快本地決策但不繞過監督。你應首先實施什麼？",
         [("A delegated decision-rights matrix within the project governance framework", "在專案治理架構中建立委派決策權限矩陣"),
          ("A weekly status email to the PMO without changing decision structures", "向 PMO 發送每週狀態郵件而不改變決策結構"),
          ("Removal of the steering committee to reduce approval layers", "移除指導委員會以減少核准層級"),
          ("A new risk register entry for vendor disputes only", "僅在風險登記冊新增供應商爭議項目")],
         0,
         "Governance balances speed with accountability through clear decision rights. A delegated matrix specifies local versus escalated authorities while preserving PMO oversight. Status emails inform but do not define authority. Removing the steering committee eliminates strategic oversight. A risk register entry tracks threats but does not establish decision pathways. Effective governance clarifies who decides, not merely who is informed.",
         "治理透過明確決策權限平衡速度與問責。委派矩陣規定本地與升級權限，保留 PMO 監督。狀態郵件僅告知，不建立權限。移除指導委員會會失去策略監督。風險登記冊追蹤威脅，不建立決策路徑。有效治理釐清誰做決定。",
         ["governance", "PMO"]),
        ("During a stage-gate review for a {ind} project, the portfolio board questions whether continued funding aligns with organizational strategic pillars. Which artifact best demonstrates alignment?",
         "在 {ind_zh} 專案階段關卡審查中，組合委員會質疑持續資金是否與組織策略支柱對齊。哪份產出物最能證明對齊？",
         [("A benefits traceability matrix linking deliverables to strategic objectives and KPIs", "將交付物連結策略目標與 KPI 的效益追溯矩陣"),
          ("The detailed project schedule showing critical path activities", "顯示關鍵路徑活動的詳細專案時程"),
          ("The team charter describing internal roles", "描述內部角色的團隊章程"),
          ("The issue log listing open defects", "列出未關閉缺陷的問題日誌")],
         0,
         "Portfolio governance evaluates strategic fit through traceable benefits. A benefits traceability matrix maps deliverables to strategic pillars and measurable outcomes. The schedule shows timing but not strategic value. The team charter defines internal roles, not organizational alignment. The issue log reflects execution problems, not strategic fit. Governance boards need evidence that investments deliver intended organizational value.",
         "組合治理透過可追溯效益評估策略契合。效益追溯矩陣對應交付物至策略支柱與可衡量成果。時程顯示時間點非策略價值。團隊章程定義內部角色。問題日誌反映執行問題。治理委員會需要投資能交付組織價值的證據。",
         ["governance", "portfolio-alignment"]),
        ("Your {ind} program has three interdependent projects sharing a governance board. One project manager routinely makes scope decisions without board approval, causing downstream conflicts. What is the best corrective action?",
         "你的 {ind_zh} 計畫有三個相互依賴專案共用治理委員會。一位專案經理經常未經委員會核准即做範圍決策，造成下游衝突。最佳糾正措施是什麼？",
         [("Clarify and communicate decision rights in the governance framework and require board approval for cross-project scope changes", "在治理架構中釐清並溝通決策權限，跨專案範圍變更須經委員會核准"),
          ("Replace the project manager immediately without reviewing governance documents", "不審查治理文件即立即更換專案經理"),
          ("Allow the behavior to continue to maintain schedule velocity", "允許行為繼續以維持時程速度"),
          ("Merge all three projects into one without governance changes", "在不改變治理的情況下合併三個專案")],
         0,
         "Governance failures often stem from unclear decision rights rather than individual misconduct alone. Clarifying and communicating the governance framework ensures scope decisions with cross-project impact receive appropriate oversight. Replacing a PM without fixing systemic gaps may repeat the problem. Tolerating unauthorized decisions erodes portfolio integrity. Merging projects without governance redesign does not address accountability. Governance boards exist to coordinate interdependent decisions.",
         "治理失敗常源於決策權限不清。釐清並溝通治理架構確保跨專案影響的範圍決策獲適當監督。僅更換 PM 未修正系統缺口可能重複問題。容忍未授權決策會侵蚀組合完整性。合併專案未重新設計治理無法解決問責。治理委員會用於協調相互依賴決策。",
         ["governance", "decision-rights"]),
        ("The PMO introduces a new project classification model. Your {proj} is reclassified from tier-two to tier-one, triggering additional reporting and gate requirements. What should you do first?",
         "PMO 推出新專案分類模型。你的 {proj_zh} 從二級重分類為一級，觸發額外報告與關卡要求。你應首先做什麼？",
         [("Review the updated PMO standards and align the project governance plan and reporting cadence accordingly", "審查更新後 PMO 標準並相應調整專案治理計畫與報告節奏"),
          ("Ignore the reclassification until the next audit", "忽略重分類直到下次稽核"),
          ("Request exemption from all tier-one requirements", "要求豁免所有一級要求"),
          ("Reduce project scope to return to tier-two classification", "縮減範圍以回到二級分類")],
         0,
         "PMO classification changes define governance expectations. Reviewing updated standards and aligning the governance plan ensures compliance and appropriate oversight from the reclassification date. Ignoring changes creates audit findings and misaligned reporting. Requesting blanket exemptions without justification undermines portfolio consistency. Reducing scope solely to avoid governance is a poor business decision. PMO alignment is a governance responsibility of the project manager.",
         "PMO 分類變更定義治理期望。審查更新標準並調整治理計畫確保合規與適當監督。忽略變更會產生稽核發現與報告錯位。無理由要求全面豁免會破壞組合一致性。僅為迴避治理而縮減範圍是錯誤業務決策。PMO 對齊是專案經理的治理責任。",
         ["governance", "PMO"]),
        ("At project initiation for a {ind} transformation, the sponsor asks how project performance will be overseen relative to organizational policies. Which response is most appropriate?",
         "在 {ind_zh} 轉型專案啟動時，贊助者詢問專案績效如何依組織政策受監督。哪項回應最適當？",
         [("Describe the governance structure including oversight bodies, reporting frequency, and escalation paths defined in the project charter and governance plan", "說明專案章程與治理計畫中定義的監督機構、報告頻率與升級路徑之治理結構"),
          ("Promise daily informal updates without formal governance structures", "承諾每日非正式更新而無正式治理結構"),
          ("Defer governance discussions until execution begins", "延後治理討論至執行開始"),
          ("State that agile projects do not require governance oversight", "表示敏捷專案不需要治理監督")],
         0,
         "Project initiation establishes how performance is overseen. Describing governance structures, reporting cadence, and escalation paths in the charter and governance plan sets clear expectations aligned with organizational policies. Informal updates alone lack auditability. Deferring governance leaves oversight gaps during early decisions. Claiming agile projects need no governance is incorrect—all delivery approaches require appropriate oversight scaled to context.",
         "專案啟動建立績效監督方式。在章程與治理計畫中說明治理結構、報告節奏與升級路徑，設定與組織政策對齊的期望。僅非正式更新缺乏可稽核性。延後治理會在早期決策留下監督缺口。宣稱敏捷不需治理是錯誤的——所有交付方式都需適當監督。",
         ["governance", "oversight"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[idx % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be1_multi(idx):
    templates = [
        ("Your organization is establishing governance for a multi-project {ind} portfolio. Select TWO activities that should be defined at the portfolio governance level.",
         "組織正為多專案 {ind_zh} 組合建立治理。請選兩項應在組合治理層級定義的活動。",
         [("Decision rights and escalation paths for inter-project dependencies", "跨專案依賴的決策權限與升級路徑"),
          ("Standard stage-gate criteria aligned with strategic investment priorities", "與策略投資優先順序對齊的標準階段關卡準則"),
          ("Daily task assignments for each project team member", "每位專案團隊成員的每日任務指派"),
          ("Individual sprint retrospectives for every project team", "每個專案團隊的個別衝刺回顧"),
          ("Ad hoc scope approvals by any project manager without documentation", "任何專案經理無文件化的臨時範圍核准")],
         [0, 1],
         "Portfolio governance defines cross-project decision rights and standard gate criteria aligned with strategy. These structures enable consistent oversight across the portfolio. Daily task assignments are team-level operational activities. Sprint retrospectives are team improvement practices, not portfolio governance. Ad hoc undocumented approvals violate governance principles. Portfolio governance operates at a higher level than project or team management.",
         "組合治理定義跨專案決策權限與與策略對齊的標準關卡準則，使組合一致監督。每日任務指派是團隊營運活動。衝刺回顧是團隊改善實務，非組合治理。臨時無文件核准違反治理原則。組合治理層級高於專案或團隊管理。",
         ["governance", "portfolio"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[idx % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = [(c - shift) % n for c in t[3]]
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, sorted(correct), t[4], t[5], t[6])

def get_be2_mcq(idx):
    templates = [
        ("Your {ind} project processes customer PII. The compliance officer informs you that updated data privacy regulations take effect before user acceptance testing. The product owner wants to defer compliance work to protect velocity. What should you do first?",
         "你的 {ind_zh} 專案處理客戶 PII。合規長通知更新資料隱私法規將在 UAT 前生效。產品負責人希望延後合規工作以維持速度。你應首先做什麼？",
         [("Facilitate a discussion with legal, the product owner, and the team to assess regulatory impact and reprioritize accordingly", "促進法務、產品負責人與團隊討論，評估法規影響並重新排序"),
          ("Accept deferral because the team owns the backlog", "接受延後，因團隊擁有待辦清單"),
          ("Escalate to senior management without team consultation", "未諮詢團隊即向高階管理層升級"),
          ("Document the gap in lessons learned and address after release", "在經驗教訓中記錄缺口，發布後再處理")],
         0,
         "Compliance requirements are non-negotiable constraints requiring assessment before prioritization. Cross-functional discussion ensures legal obligations are understood and the backlog adjusted with informed consent. Accepting deferral without analysis exposes the organization to penalties. Escalating without team input wastes time. Recording gaps for later does not mitigate exposure before release. All delivery approaches operate within regulatory boundaries.",
         "合規要求是不可協商約束，須在優先排序前評估。跨職能討論確保理解法律義務並在知情下調整待辦清單。未分析即延後會面臨處罰。未徵詢團隊即升級浪費時間。僅記錄缺口無法在發布前降低暴露。所有交付方式都須在法規界限內運作。",
         ["compliance", "regulatory"]),
        ("An internal audit for your {proj} finds incomplete safety documentation for contractor work on-site. Regulatory inspection is scheduled in three weeks. What is the best immediate action?",
         "你的 {proj_zh} 內部稽核發現承包商現場作業安全文件不完整。監管檢查三週後進行。最佳立即行動是什麼？",
         [("Initiate a corrective action plan with contractors to complete safety documentation and verify audit readiness before inspection", "與承包商啟動矯正行動計畫，完成安全文件並在檢查前驗證稽核就緒度"),
          ("Request postponement of the regulatory inspection indefinitely", "無限期要求延後監管檢查"),
          ("Proceed with work and update documentation after inspection", "繼續作業，檢查後再更新文件"),
          ("Transfer audit responsibility entirely to contractors without oversight", "將稽核責任完全轉移給承包商而不監督")],
         0,
         "Audit readiness for safety standards requires proactive corrective action. A structured plan with contractors to complete documentation and verify readiness addresses the finding before inspection. Indefinite postponement is rarely granted and does not fix gaps. Proceeding without documentation creates safety and legal violations. Transferring responsibility without oversight leaves the organization accountable for contractor compliance failures.",
         "安全標準稽核就緒需要主動矯正行動。與承包商完成文件並驗證就緒度的結構化計畫可在檢查前解決發現。無限期延後很少獲准且不修正缺口。無文件繼續作業會違反安全與法規。無監督轉移責任仍使組織對承包商合規失敗負責。",
         ["compliance", "audit-readiness"]),
        ("Your team is preparing for SOC 2 certification as part of a {ind} cloud migration. A developer proposes storing audit logs in an unapproved personal cloud account to meet a deadline. What should you do?",
         "團隊正為 {ind_zh} 雲端遷移準備 SOC 2 認證。開發者提議將稽核日誌存放在未核准的個人雲端帳戶以趕期限。你應怎麼做？",
         [("Stop the action, explain the compliance violation, and work with the team to find an approved logging solution", "停止行動，說明合規違規，與團隊尋找核准的日誌解決方案"),
          ("Allow it temporarily and migrate logs after certification", "暫時允許，認證後再遷移日誌"),
          ("Report the developer to HR without addressing the underlying deadline pressure", "向人資檢舉開發者而不處理期限壓力"),
          ("Ignore the proposal because certification is an IT department concern", "忽略提案，因認證是 IT 部門事務")],
         0,
         "Compliance cannot be compromised for schedule convenience. Stopping the violation, educating the team, and finding approved solutions maintains audit integrity. Temporary workarounds often become permanent and fail certification. Reporting individuals without addressing systemic deadline pressure misses root causes. Certification scope includes project deliverables—the project manager ensures compliance requirements are met.",
         "合規不可為時程便利而妥協。停止違規、教育團隊並尋找核准方案維持稽核完整性。暫時變通常變永久且無法通過認證。僅檢舉個人未處理系統性期限壓力。認證範圍包含專案交付物——專案經理確保合規要求達成。",
         ["compliance", "SOC2"]),
        ("During execution of a {ind} project, legal discovers that a vendor contract lacks required anti-bribery clauses mandated by corporate policy. The vendor refuses renegotiation citing the signed agreement. What should you do first?",
         "在 {ind_zh} 專案執行中，法務發現供應商合約缺少公司政策要求的反賄賂條款。供應商以已簽合約為由拒絕重新談判。你應首先做什麼？",
         [("Escalate to the contract administrator and legal counsel to assess compliance risk and determine whether work must pause pending contract remediation", "升級至合約管理員與法律顧問評估合規風險，決定是否須暫停作業待合約修正"),
          ("Continue work because the contract is legally binding", "繼續作業，因合約具法律約束力"),
          ("Terminate the vendor immediately without legal review", "未經法律審查即立即終止供應商"),
          ("Document the gap and address it at project closure", "記錄缺口，專案結束時再處理")],
         0,
         "Corporate anti-bribery requirements are mandatory compliance obligations. Escalating to legal and contract administration enables a risk-based decision on whether work can continue. Continuing without required clauses exposes the organization to regulatory and reputational harm. Immediate termination without legal review may breach contract terms. Deferring to closure leaves ongoing compliance violations unaddressed during active work.",
         "公司反賄賂要求是強制合規義務。升級至法務與合約管理可風險導向決定是否繼續作業。缺少必要條款仍繼續會造成監管與聲譽損害。未經法律審查即終止可能違約。延至結束會使進行中違規未處理。",
         ["compliance", "contract"]),
        ("Quality assurance discovers that test data in your {proj} includes unmasked production PII, violating data handling standards. What is the most appropriate response?",
         "品質保證發現你的 {proj_zh} 測試資料含未遮罩的生產 PII，違反資料處理標準。最適當回應是什麼？",
         [("Immediately isolate the data, notify the data protection officer, and implement approved masking procedures before resuming testing", "立即隔離資料、通知資料保護長，並在恢復測試前實施核准遮罩程序"),
          ("Continue testing since the data helps ensure realistic results", "繼續測試，因資料有助真實結果"),
          ("Delete all test environments without documenting the incident", "刪除所有測試環境而不記錄事件"),
          ("Wait for the next scheduled compliance review to report the issue", "等到下次排定合規審查再報告")],
         0,
         "PII violations require immediate containment and notification per data protection standards. Isolating data, engaging the DPO, and implementing approved masking addresses the violation before further exposure. Continuing testing compounds the breach. Deleting environments without documentation destroys audit evidence. Waiting for scheduled reviews delays mandatory breach response timelines. Compliance demands prompt corrective action when standards are violated.",
         "PII 違規須依資料保護標準立即 containment 與通知。隔離資料、聯繫 DPO 並實施遮罩可在進一步暴露前處理。繼續測試加劇外洩。無文件刪除環境會破壞稽核證據。等待排定審查會延遲強制回應時限。",
         ["compliance", "data-protection"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 2) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be2_multi(idx):
    templates = [
        ("Your {ind} project must achieve audit readiness before go-live. Select TWO activities that demonstrate proactive compliance preparation.",
         "你的 {ind_zh} 專案須在上線前達成稽核就緒。請選兩項能展現主動合規準備的活動。",
         [("Conduct a compliance gap assessment against applicable regulations and corporate policies", "對適用法規與公司政策進行合規差距評估"),
          ("Establish traceable evidence collection for control activities throughout the project lifecycle", "在專案生命週期建立可追蹤的控制活動證據收集"),
          ("Defer all compliance documentation until after go-live", "將所有合規文件延至上線後"),
          ("Rely solely on vendor self-certifications without independent verification", "僅依賴供應商自我認證而不獨立驗證"),
          ("Exclude the compliance officer from project planning sessions", "將合規長排除在專案規劃會議外")],
         [0, 1],
         "Proactive audit readiness requires gap assessments and traceable evidence throughout the lifecycle. These activities identify deficiencies early and build the documentation auditors need. Deferring documentation creates last-minute failures. Vendor self-certifications alone may not satisfy regulatory requirements. Excluding compliance officers from planning guarantees gaps. Compliance is integrated into project execution, not bolted on at the end.",
         "主動稽核就緒需要差距評估與生命週期內可追蹤證據，早期識別不足並建立稽核所需文件。延後文件會造成最後關頭失敗。僅供應商自證可能不符監管要求。排除合規長會保證缺口。合規整合於專案執行，非結尾才加上。",
         ["compliance", "audit-readiness"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 2) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be3_mcq(idx):
    templates = [
        ("A hybrid {ind} implementation uses a predictive baseline for infrastructure while configuration follows two-week sprints. A change request adds a new integration module affecting both the fixed milestone schedule and three sprint backlogs. What is the most appropriate first step?",
         "混合式 {ind_zh} 導入以預測式基線管理基礎設施，設定採兩週衝刺。變更請求新增整合模組，同時影響固定里程碑與三個衝刺待辦清單。最適當的第一步是什麼？",
         [("Submit the change through integrated change control and assess impacts on both the predictive baseline and agile backlogs", "透過整合變更控制提交變更，評估對預測式基線與敏捷待辦清單的影響"),
          ("Add integration stories directly to the next sprint without formal review", "未經正式審查直接將整合故事加入下一衝刺"),
          ("Reject the change because the predictive baseline cannot be modified", "拒絕變更，因預測式基線不可修改"),
          ("Implement the module as a workaround and update documentation at closure", "以變通實作模組，結束時再更新文件")],
         0,
         "Hybrid projects require unified change control evaluating impacts across predictive and adaptive streams. Integrated change control ensures scope, schedule, cost, and backlog priorities are assessed before commitment. Adding stories without review bypasses governance. Rejecting all baseline changes ignores legitimate needs. Workarounds create technical debt. The change control board should decide based on holistic impact analysis.",
         "混合式專案需要統一變更控制評估預測式與適應式工作流影響。整合變更控制確保承諾前評估範圍、時程、成本與待辦清單。未審查加故事繞過治理。拒絕所有基線變更忽略合法需求。變通造成技術債。變更管制委員會(CCB)應依全面影響分析決定。",
         ["change-management", "CCB"]),
        ("A key stakeholder requests a new reporting dashboard during sprint execution for your {proj}. The product owner agrees it is valuable but the team estimates it exceeds remaining sprint capacity. The stakeholder threatens to withdraw funding if not delivered this sprint. What should you do?",
         "關鍵利害關係人在 {proj_zh} 衝刺執行中要求新報表儀表板。產品負責人認同有價值但團隊估計超出剩餘容量。利害關係人威脅本衝刺未交付將撤回資金。你應怎麼做？",
         [("Support the product owner in facilitating a transparent trade-off discussion, documenting scope swap options and escalating funding concerns to the sponsor if needed", "支持產品負責人引導透明取捨討論，記錄範圍交換選項，必要時將資金疑慮升級贊助者"),
          ("Instruct the team to work weekends to deliver without removing committed work", "指示團隊週末加班交付且不移除已承諾工作"),
          ("Accept the change silently and defer previously committed stories without notification", "默默接受變更並未通知地延後已承諾故事"),
          ("Reject the request outright because scope is frozen during a sprint", "因衝刺期間範圍凍結而直接拒絕")],
         0,
         "Agile change control protects sprint commitments while enabling transparent negotiation. The product owner owns backlog prioritization; the project manager facilitates stakeholder communication and escalates funding threats to the sponsor. Forcing overtime without trade-offs violates sustainable pace. Silently swapping scope breaks trust. Outright rejection ignores business value. Balance agility with governance through visible trade-off decisions.",
         "敏捷變更控制保護衝刺承諾並促成透明協商。產品負責人擁有優先排序；專案經理促進溝通並升級資金威脅。無取捨加班違反永續節奏。默默交換範圍破壞信任。直接拒絕忽略業務價值。透過可見取捨平衡敏捷與治理。",
         ["change-management", "CCB"]),
        ("The CCB for your {ind} project receives a change request that would reduce testing scope by two weeks but increase post-go-live defect risk. The sponsor is unavailable for two days. What should you do?",
         "你的 {ind_zh} 專案 CCB 收到將測試範圍縮減兩週但增加上線後缺陷風險的變更請求。贊助者兩天內無法聯繫。你應怎麼做？",
         [("Present the change with documented impact analysis to the CCB, noting the risk trade-off and requesting a decision within the governance timeline", "向 CCB 呈現附文件化影響分析的變更，說明風險取捨並請求在治理時限內決定"),
          ("Approve the change yourself to avoid schedule delay", "自行核准變更以避免時程延遲"),
          ("Reject the change automatically because the sponsor is unavailable", "因贊助者不在而自動拒絕"),
          ("Implement the scope reduction without CCB review to meet the deadline", "未經 CCB 審查即實施範圍縮減以趕期限")],
         0,
         "Change control boards exist to evaluate trade-offs when sponsors are temporarily unavailable. Presenting documented impact analysis enables the CCB to decide based on risk appetite and governance authority. Self-approval exceeds project manager authority for scope-risk trade-offs. Automatic rejection ignores legitimate business needs. Implementing without review violates change control policy and accountability.",
         "變更管制委員會在贊助者暫時不在時評估取捨。呈現文件化影響分析使 CCB 依風險偏好與治理權限決定。自行核准超出 PM 對範圍風險取捨的權限。自動拒絕忽略合法需求。未審查實施違反變更控制政策。",
         ["change-management", "impact-analysis"]),
        ("Mid-project, regulatory changes require modifications to your {proj} deliverables. The change request estimates four weeks of additional work. The baseline contract allows CCB-approved changes but the client has not yet signed the formal change order. What should you do first?",
         "專案中期，法規變更要求修改 {proj_zh} 交付物。變更請求估計額外四週工作。基線合約允許 CCB 核准變更但客戶尚未簽署正式變更令。你應首先做什麼？",
         [("Ensure the CCB approves the change internally and initiate client change order processing before committing team resources", "確保 CCB 內部核准變更並在投入團隊資源前啟動客戶變更令流程"),
          ("Begin work immediately because regulatory compliance is mandatory", "立即開始作業，因法規合規是強制的"),
          ("Wait indefinitely for the client signature before any internal analysis", "在客戶簽署前無限期等待而不做任何內部分析"),
          ("Absorb the four weeks of work without documenting a change request", "吸收四週工作而不記錄變更請求")],
         0,
         "Regulatory-driven changes still require formal change control. CCB approval with parallel client change order processing ensures internal governance and contractual alignment before resource commitment. Starting work without approval creates scope creep and billing disputes. Waiting without analysis delays compliance unnecessarily. Absorbing work without documentation erodes baseline integrity and hides true project performance.",
         "法規驅動的變更仍須正式變更控制。CCB 核准並平行處理客戶變更令，確保投入資源前內部治理與合約對齊。未核准即開工造成範圍蔓延與帳務爭議。未分析即等待不必要延遲合規。無文件吸收工作侵蚀基線完整性。",
         ["change-management", "CCB"]),
        ("Your {ind} agile release train has accumulated seventeen approved change requests in the backlog grooming queue. The product owner wants to batch them into one sprint. What is the best approach?",
         "你的 {ind_zh} 敏捷發布列車在待辦清單梳理佇列累積十七項已核准變更請求。產品負責人希望批次放入一個衝刺。最佳方法是什麼？",
         [("Facilitate prioritization with the product owner, grouping related changes while respecting team capacity and dependency order", "與產品負責人促進優先排序，分組相關變更並尊重團隊容量與依賴順序"),
          ("Force all seventeen changes into the current sprint regardless of capacity", "不論容量強制十七項變更全部放入本衝刺"),
          ("Discard older change requests to reduce queue size", "丟棄較舊變更請求以縮小佇列"),
          ("Defer all changes until the next program increment planning", "將所有變更延至下一方案增量規劃")],
         0,
         "Approved changes require thoughtful prioritization, not arbitrary batching or deferral. Grouping related changes while respecting capacity and dependencies optimizes flow without overloading the team. Forcing all changes into one sprint violates sustainable pace and quality. Discarding approved changes ignores stakeholder commitments. Deferring everything delays approved business value. Change management integrates with backlog refinement practices.",
         "已核准變更需要審慎優先排序，非任意批次或延後。分組相關變更並尊重容量與依賴可優化流程。強制全部放入一衝刺違反永續節奏與品質。丟棄已核准變更忽略利害關係人承諾。全部延後延遲已核准業務價值。變更管理整合待辦清單梳理。",
         ["change-management", "backlog"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 4) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be3_multi(idx):
    templates = [
        ("For a {ind} project using formal change control, select TWO elements that must be included in a change request before CCB review.",
         "對使用正式變更控制的 {ind_zh} 專案，請選兩項變更請求在 CCB 審查前必須包含的元素。",
         [("Impact analysis on scope, schedule, cost, and quality", "對範圍、時程、成本與品質的影響分析"),
          ("Clear description of the proposed change and business justification", "擬議變更的清楚描述與業務理由"),
          ("Informal verbal approval from a team member", "團隊成員的非正式口頭核准"),
          ("Automatic approval if submitted before Friday", "週五前提交即自動核准"),
          ("Implementation completion report", "實施完成報告")],
         [0, 1],
         "Change requests require impact analysis and clear justification before CCB review enables informed decisions. These elements support traceability and accountability. Verbal approvals lack documentation required for governance. Automatic approval by deadline violates change control principles. Implementation reports come after approval, not before. The CCB evaluates proposed changes based on documented impacts and business rationale.",
         "變更請求在 CCB 審查前須有影響分析與清楚理由以支持知情決策。口頭核准缺乏治理所需文件。依截止日自動核准違反變更控制原則。實施報告在核准後而非之前。CCB 依文件化影響與業務理由評估擬議變更。",
         ["change-management", "CCB"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 4) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be4_mcq(idx):
    templates = [
        ("During a daily stand-up on your {proj}, a developer reports that a third-party API license expired, blocking two in-progress stories. What should you do first?",
         "在 {proj_zh} 每日站會中，開發者回報第三方 API 授權到期，阻礙兩個進行中故事。你應首先做什麼？",
         [("Work with the product owner to reorder blocked stories and initiate procurement or vendor contact to restore the license", "與產品負責人重排受阻故事，啟動採購或聯繫供應商恢復授權"),
          ("Wait until the next sprint planning to address the blocker", "等到下次衝刺規劃再處理阻礙"),
          ("Assign the developer to work overtime until a workaround is coded", "指派開發者加班直到寫出變通方案"),
          ("Record the issue in the risk register and continue without changes", "在風險登記冊記錄問題並繼續不變")],
         0,
         "An expired license is an active impediment blocking delivery now. The project manager should help adapt immediately by adjusting priorities and resolving the external dependency. Waiting for sprint planning delays value unnecessarily. Forcing overtime addresses symptoms, not root cause. Recording only in the risk register treats a current blocker as hypothetical. Agile teams escalate impediments promptly to restore flow.",
         "授權到期是當前阻礙交付的障礙。專案經理應立即調整優先順序並解決外部依賴。等到衝刺規劃不必要延遲價值。強迫加班只處理症狀。僅在風險登記冊記錄會把當前阻礙當假設事件。敏捷團隊應及時升級障礙以恢復流程。",
         ["impediments", "blockers"]),
        ("In a hybrid {ind} product launch, the predictive workstream is on schedule but the agile team found a critical security flaw requiring two extra sprints. Marketing announced the launch date publicly. What should you do first?",
         "混合式 {ind_zh} 產品上市中，預測式工作流按時程但敏捷團隊發現需額外兩衝刺修復的關鍵安全漏洞。行銷已公開宣布上市日期。你應首先做什麼？",
         [("Convene a cross-workstream issue review with the sponsor, security, and marketing to assess impact and determine whether the launch date must change", "召集跨工作流問題審查，與贊助者、資安及行銷評估影響並決定上市日期是否須變更"),
          ("Release on the announced date with a plan to patch post-launch", "按宣布日期發布並計畫上市後修補"),
          ("Cancel the agile workstream and transfer fixes to the predictive team", "取消敏捷工作流並將修復轉交預測式團隊"),
          ("Instruct marketing to proceed while the team works in secret to meet the date", "指示行銷繼續，開發團隊秘密趕工")],
         0,
         "A critical security flaw is a business-level issue affecting launch readiness. Cross-workstream review brings sponsor authority, security expertise, and marketing commitments together for an informed decision. Releasing with a known critical flaw creates legal and reputational harm. Canceling agile mid-flight disrupts ownership without guaranteed gains. Secret crunching hides risk from stakeholders. Issue management at this scale requires transparent escalation.",
         "關鍵安全漏洞是影響上市就緒的業務層級問題。跨工作流審查匯集贊助者、資安與行銷以做出知情決策。已知關鍵漏洞仍發布會造成法律與聲譽損害。中途取消敏捷擾亂責任。秘密趕工向利害關係人隱藏風險。此規模問題管理需要透明升級。",
         ["impediments", "escalation"]),
        ("Your {ind} project issue log shows three recurring impediments related to slow procurement approvals, each resolved temporarily but returning within two sprints. What is the best next step?",
         "你的 {ind_zh} 專案問題日誌顯示三項與採購核准緩慢相關的重複障礙，每次暫時解決但兩衝刺內復現。最佳下一步是什麼？",
         [("Escalate the systemic procurement bottleneck to the sponsor and PMO with data from the issue log to pursue a permanent process fix", "依問題日誌數據向贊助者與 PMO 升級系統性採購瓶頸以尋求永久流程修正"),
          ("Continue resolving each instance locally without escalation", "繼續本地解決每個實例而不升級"),
          ("Stop logging recurring issues to reduce administrative burden", "停止記錄重複問題以減少行政負擔"),
          ("Assign a team member to bypass procurement entirely", "指派成員完全繞過採購")],
         0,
         "Recurring impediments signal systemic issues beyond team-level resolution. Escalating with issue log data enables sponsor and PMO action on permanent process improvements. Local fixes alone waste repeated effort. Stopping logging hides patterns needed for improvement. Bypassing procurement violates organizational controls and creates compliance risk. Effective issue management analyzes patterns and escalates root causes.",
         "重複障礙表示超出團隊層級的系統性問題。依問題日誌升級使贊助者與 PMO 可永久修正流程。僅本地修正浪費重複努力。停止記錄隱藏改善所需模式。繞過採購違反組織控制並造成合規風險。有效問題管理分析模式並升級根本原因。",
         ["impediments", "issue-log"]),
        ("A vendor on your {proj} stops responding to critical defect reports, blocking integration testing for five days. The contract specifies escalation to the vendor account manager after 48 hours of non-response. What should you do?",
         "你的 {proj_zh} 供應商停止回應關鍵缺陷報告，阻礙整合測試五天。合約規定 48 小時未回應須升級至供應商客戶經理。你應怎麼做？",
         [("Follow the contract escalation path, document all communication in the issue log, and notify the sponsor of schedule impact", "依合約升級路徑，在問題日誌記錄所有溝通，並通知贊助者時程影響"),
          ("Find an alternative vendor without contract review", "未審查合約即尋找替代供應商"),
          ("Skip integration testing and proceed to deployment", "跳過整合測試直接部署"),
          ("Wait passively for the vendor to respond eventually", "被動等待供應商最終回應")],
         0,
         "Contractual escalation paths exist for vendor non-performance. Following defined procedures, documenting in the issue log, and informing the sponsor of impact ensures accountability and enables recovery decisions. Switching vendors without contract review may breach terms. Skipping testing creates quality and security risks. Passive waiting beyond contract thresholds wastes schedule without leveraging available remedies.",
         "合約升級路徑用於供應商未履約。依定義程序、在問題日誌記錄並通知贊助者影響，確保問責並支持恢復決策。未審查即換供應商可能違約。跳過測試造成品質與安全風險。超出合約門檻仍被動等待浪費時程。",
         ["impediments", "escalation"]),
        ("The {ind} deployment team reports that production access credentials were revoked by IT security during a company-wide audit, halting the release pipeline. What is the most appropriate immediate action?",
         "{ind_zh} 部署團隊回報 IT 資安在全公司稽核中撤銷生產存取憑證，Release pipeline 停擺。最適當的立即行動是什麼？",
         [("Log the impediment, contact IT security to understand remediation requirements, and work with the product owner to adjust the release plan", "記錄障礙、聯繫 IT 資安了解修復要求，並與產品負責人調整發布計畫"),
          ("Use personal credentials to unblock the pipeline temporarily", "使用個人憑證暫時解除 pipeline 阻礙"),
          ("Cancel the release permanently", "永久取消發布"),
          ("Ignore the revocation and continue deployment in the test environment only", "忽略撤銷僅在測試環境繼續部署")],
         0,
         "Revoked credentials during an audit are a legitimate security control, not a team failure. Logging the impediment, engaging IT security for remediation requirements, and adjusting the release plan addresses the blocker through proper channels. Using personal credentials violates security policy. Canceling permanently overreacts to a likely temporary block. Ignoring revocation in test does not resolve the production release impediment.",
         "稽核中撤銷憑證是合法資安控制，非團隊失敗。記錄障礙、聯繫 IT 資安並調整發布計畫可經適當管道處理。使用個人憑證違反資安政策。永久取消對暫時阻礙反應過度。忽略撤銷無法解決生產發布障礙。",
         ["impediments", "blockers"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 1) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be4_multi(idx):
    templates = [
        ("Your {ind} project team faces persistent external blockers. Select TWO appropriate uses of the issue log in this situation.",
         "你的 {ind_zh} 專案團隊面臨持續外部阻礙。請選兩項在此情況下問題日誌的適當用途。",
         [("Track impediment history, owners, and resolution status to identify escalation patterns", "追蹤障礙歷史、負責人與解決狀態以識別升級模式"),
          ("Document impact on schedule and deliverables to support sponsor decisions", "記錄對時程與交付物的影響以支持贊助者決策"),
          ("Replace all verbal team communication entirely", "完全取代所有口頭團隊溝通"),
          ("Store only closed issues and delete open blockers", "僅存放已關閉問題並刪除開放阻礙"),
          ("Use the log exclusively for budget tracking", "僅用日誌做預算追蹤")],
         [0, 1],
         "Issue logs support impediment tracking with history and ownership for pattern analysis and escalation. Documenting schedule and deliverable impact provides sponsors factual basis for decisions. Replacing all verbal communication is impractical and slows resolution. Deleting open blockers destroys accountability. Budget tracking belongs in cost management tools, not the issue log. Effective issue management uses the log as a transparent record for resolution and escalation.",
         "問題日誌以歷史與責任追蹤障礙以分析模式與升級。記錄時程與交付物影響為贊助者提供決策事實基礎。完全取代口頭溝通不實際且減緩解決。刪除開放阻礙破壞問責。預算追蹤屬成本管理工具。有效問題管理以日誌作透明記錄。",
         ["impediments", "issue-log"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 1) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be5_mcq(idx):
    templates = [
        ("Your organization evaluates a {ind} data-center migration. The business case shows strong ROI, but assessment reveals a single vendor failure could cause extended downtime on revenue-critical systems. The sponsor wants a go/no-go decision at next week's gate review. What should you recommend?",
         "組織評估 {ind_zh} 資料中心遷移。商業案例 ROI 強勁，但評估顯示單一供應商故障可能長時間停機影響營收關鍵系統。贊助者希望下週關卡審查做 go/no-go 決策。你應建議什麼？",
         [("Present the business case with quantitative risk analysis and response strategies, recommending conditional proceed pending mitigation validation", "呈現商業案例與量化風險分析及應對策略，建議在緩解驗證完成前有條件 proceed"),
          ("Recommend immediate no-go because any single-point-of-failure risk is unacceptable", "因任何單點故障風險不可接受而建議立即 no-go"),
          ("Recommend proceed based on ROI alone because risk is handled during execution", "僅依 ROI 建議 proceed，因風險在執行階段處理"),
          ("Defer the gate review until all vendor contracts are renegotiated", "在所有供應商合約重談完成前延後關卡審查")],
         0,
         "Gate reviews require balanced input: benefits, costs, and risks together. Quantitative risk analysis with proposed responses allows conditional proceed while requiring mitigation proof. Automatic no-go ignores manageable risks and business value. Proceeding on ROI alone violates integrated decision-making. Indefinite deferral stalls the portfolio without resolving risk. Conditional approval with exit criteria is mature governance.",
         "關卡審查需平衡效益、成本與風險。量化風險分析與應對策略可有條件 proceed 並要求緩解證明。自動 no-go 忽略可管理風險與業務價值。僅依 ROI proceed 違反整合決策。無限期延後使組合停滯。附退出條件的有條件核准是成熟治理。",
         ["risk", "quantitative-analysis"]),
        ("During {proj} planning, the team identifies a threat of key personnel departure during a critical integration phase. Qualitative analysis rates probability as medium and impact as high. What response strategy is most appropriate?",
         "在 {proj_zh} 規劃中，團隊識別關鍵整合階段關鍵人員離職威脅。定性分析機率中、影響高。最適當的應對策略是什麼？",
         [("Mitigate by cross-training team members and documenting critical knowledge before the integration phase", "透過交叉培訓與在整合階段前文件化關鍵知識來減輕"),
          ("Accept the risk without action because personnel decisions are outside project control", "不採行動而接受風險，因人員決策超出專案控制"),
          ("Transfer the risk by requiring all team members to sign retention contracts", "要求所有成員簽署留任合約以轉移風險"),
          ("Avoid the risk by canceling the integration phase entirely", "完全取消整合階段以規避風險")],
         0,
         "Medium probability with high impact warrants active mitigation. Cross-training and knowledge documentation reduces dependency on single individuals before the critical phase. Passive acceptance ignores a manageable threat. Retention contracts may help but transfer alone does not address knowledge concentration during integration. Avoiding the integration phase defeats project objectives. The risk register should document the mitigation plan with owners and triggers.",
         "機率中、影響高需要主動減輕。交叉培訓與知識文件化在關鍵階段前降低對個人依賴。被動接受忽略可管理威脅。留任合約有幫助但僅轉移無法解決知識集中。取消整合階段違背專案目標。風險登記冊應記錄減輕計畫與負責人。",
         ["risk", "mitigate"]),
        ("Your {ind} project risk register lists twelve high-priority threats. The sponsor asks for a Monte Carlo simulation on schedule completion before approving additional contingency budget. What should you provide?",
         "你的 {ind_zh} 專案風險登記冊列十二項高優先威脅。贊助者要求在核准額外應急預算前對完工時程做 Monte Carlo 模擬。你應提供什麼？",
         [("A quantitative analysis using three-point estimates for key schedule risks, showing probability distributions and recommended contingency", "使用關鍵時程風險三點估計的量化分析，顯示機率分布與建議應急"),
          ("A qualitative risk matrix with red-yellow-green ratings only", "僅含紅黃綠評等的定性風險矩陣"),
          ("A list of risk owners without probability or impact data", "無機率或影響數據的風險負責人清單"),
          ("An assurance that the current schedule buffer is sufficient without analysis", "未經分析即保證現有時程緩衝足夠")],
         0,
         "Monte Carlo simulation requires quantitative inputs—typically three-point estimates for schedule risks—to model probability distributions and inform contingency decisions. Qualitative matrices alone lack the numerical basis for simulation. Owner lists without probability data cannot drive modeling. Unsubstantiated buffer claims do not support budget approval. Quantitative analysis translates risk register entries into decision-ready schedule confidence levels.",
         "Monte Carlo 模擬需要量化輸入——通常為時程風險三點估計——以建模機率分布並支持應急決策。僅定性矩陣缺乏模擬數值基礎。無機率數據的負責人清單無法驅動建模。未經證明的緩衝聲明無法支持預算核准。量化分析將風險登記冊轉為決策就緒的時程信心水準。",
         ["risk", "Monte-Carlo"]),
        ("A {proj} vendor proposes fixed-price contracting, transferring cost overrun risk to the vendor. Your team identifies significant requirements uncertainty in a novel technology area. What is the best risk response regarding the contract strategy?",
         "{proj_zh} 供應商提議固定總價合約，將成本超支風險轉移給供應商。團隊在新技術領域識別重大需求不確定性。關於合約策略的最佳風險應對是什麼？",
         [("Recommend a contract structure with shared risk provisions or phased commitments rather than pure fixed-price given requirements uncertainty", "鑑於需求不確定性，建議分擔風險條款或分階段承諾的合約結構，而非純固定總價"),
          ("Accept fixed-price immediately to maximize risk transfer regardless of uncertainty", "不論不確定性立即接受固定總價以最大化風險轉移"),
          ("Avoid all vendor engagement until requirements are fully defined", "在需求完全定義前避免所有供應商合作"),
          ("Accept all cost overrun risk internally with a time-and-materials contract only", "僅以工時材料合約在內部接受所有成本超支風險")],
         0,
         "Transfer strategies must account for residual risk and vendor behavior under uncertainty. Pure fixed-price with unclear requirements often leads to vendor padding, disputes, or quality cuts. Shared-risk or phased contracts align incentives while managing uncertainty. Immediate fixed-price ignores requirements ambiguity. Avoiding vendors delays delivery. Pure time-and-materials accepts all cost risk without leveraging vendor expertise. Risk-based contracting matches structure to uncertainty level.",
         "轉移策略須考慮殘餘風險與供應商在不確定性下的行為。需求不清的純固定總價常導致加價、爭議或降品質。分擔風險或分階段合約在不確定性下對齊誘因。立即固定總價忽略需求模糊。迴避供應商延遲交付。純工時材料在內部接受全部成本風險。",
         ["risk", "transfer"]),
        ("Mid-execution of a {ind} program, a previously low-priority risk materializes as a supply chain disruption affecting three work packages. The risk register entry lacks an assigned owner. What should you do first?",
         "在 {ind_zh} 計畫執行中期，先前低優先風險以供應鏈中斷實現，影響三個工作包。風險登記冊項目缺少指定負責人。你應首先做什麼？",
         [("Activate the documented response plan if available, assign an owner, update the risk register status, and implement contingency actions", "若有文件化應對計畫則啟動、指定負責人、更新風險登記冊狀態並實施應急行動"),
          ("Remove the risk from the register since it already occurred", "因已發生而從登記冊移除風險"),
          ("Wait for the originally planned review cycle to update the register", "等到原訂審查週期再更新登記冊"),
          ("Treat it as a new issue without referencing the existing risk register entry", "當全新問題處理而不參考現有風險登記冊項目")],
         0,
         "When risks materialize, the team activates response plans, assigns ownership, and updates the register to reflect current status. Removing occurred risks loses historical data needed for lessons learned. Waiting for review cycles delays response. Ignoring the existing entry breaks traceability between identification and occurrence. The risk register remains the single source of truth throughout the risk lifecycle.",
         "風險實現時，團隊啟動應對計畫、指定責任並更新登記冊反映現況。移除已發生風險會失去經驗教訓所需歷史。等待審查週期延遲回應。忽略現有項目破壞識別與發生間的可追溯性。風險登記冊在風險生命週期內仍是單一真相來源。",
         ["risk", "risk-register"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 3) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be5_multi(idx):
    templates = [
        ("During initiation of a {ind} cloud migration, select TWO activities that establish effective risk management.",
         "在 {ind_zh} 雲端遷移啟動階段，請選兩項建立有效風險管理的活動。",
         [("Facilitate a risk identification workshop with cross-functional stakeholders including operations and security", "與包含營運及資安在內的跨職能利害關係人舉辦風險識別工作坊"),
          ("Define risk thresholds and escalation criteria aligned with organizational risk appetite", "定義與組織風險偏好對齊的風險閾值與升級準則"),
          ("Close all identified risks before the first sprint begins", "在第一次衝刺開始前關閉所有已識別風險"),
          ("Transfer all technical risks to the cloud vendor and stop tracking them", "將所有技術風險轉移給雲端供應商並停止追蹤"),
          ("Wait until the first retrospective to begin risk discussions", "等到第一次回顧會才開始風險討論")],
         [0, 1],
         "Effective risk management begins at initiation with broad identification and clear governance parameters. Cross-functional workshops surface threats early. Thresholds and escalation criteria align project handling with organizational appetite. Closing all risks at initiation is impossible. Transferring all technical risk ignores residual risks the organization owns. Deferring to retrospectives misses the planning window when responses are cheapest.",
         "有效風險管理在啟動階段以廣泛識別與明確治理參數開始。跨職能工作坊早期浮現威脅。閾值與升級準則使專案處理與組織偏好對齊。啟動時關閉所有風險不可能。轉移所有技術風險忽略組織仍須承擔的殘餘風險。延至回顧會錯失規劃窗口。",
         ["risk", "identification"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 3) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be6_mcq(idx):
    templates = [
        ("After three sprints on your {proj}, velocity is stable but customer support tickets about usability defects are rising. Retrospectives surface the same root cause—insufficient design review before coding—but no improvement sticks. What should you do next?",
         "在 {proj_zh} 三個衝刺後，速率穩定但可用性缺陷客服工單增加。回顧會反覆出現相同根本原因——編碼前設計審查不足——但改善無法持續。你應如何推動持續改善？",
         [("Facilitate a retrospective focused on one measurable improvement experiment with clear ownership and review it at the next sprint retrospective", "引導聚焦一項可衡量改善實驗的回顧會，明確責任並在下次衝刺回顧檢視"),
          ("Replace the scrum master because retrospectives are not producing results", "更換 Scrum Master，因回顧會未產生成果"),
          ("Add more stories to each sprint to create pressure for higher quality", "增加每衝刺故事數以施壓提高品質"),
          ("Skip retrospectives for two sprints to focus entirely on defect fixes", "跳過兩次衝刺回顧以全力修復缺陷")],
         0,
         "Continuous improvement works through small, owned experiments with measurable outcomes. A focused retrospective committing to one change with an owner creates accountability and learning loops. Blaming the scrum master ignores systemic gaps. Adding scope worsens quality. Skipping retrospectives removes the forum needed to solve recurring problems. Kaizen relies on inspect-and-adapt cycles.",
         "持續改善透過小型、有責任人的可衡量實驗運作。聚焦回顧會承諾一項變更並指定負責人，建立問責與學習循環。責怪 Scrum Master 忽略系統性缺口。增加範圍惡化品質。跳過回顧會移除解決反覆問題的場域。Kaizen 依賴檢視與調適循環。",
         ["continuous-improvement", "retrospective"]),
        ("Your {ind} predictive project completes phase two under budget but with twenty percent more defects than the quality baseline. The sponsor asks how you will improve before phase three. What is the best response?",
         "你的 {ind_zh} 預測式專案第二階段低於預算完成，但缺陷比品質基線多百分之二十。贊助者詢問第三階段前如何改善。最佳回應是什麼？",
         [("Conduct a lessons learned session and process analysis to identify root causes and implement targeted quality improvements in phase three planning", "進行經驗教訓與流程分析，識別根本原因並在第三階段規劃實施針對性品質改善"),
          ("Maintain the same process since the phase finished under budget", "維持相同流程，因階段低預算完成"),
          ("Increase inspection testing only without changing upstream processes", "僅增加檢驗測試而不改變上游流程"),
          ("Blame the testing team publicly to motivate better performance", "公開責怪測試團隊以激勵更好績效")],
         0,
         "Continuous improvement examines both cost and quality outcomes. Lessons learned with process analysis identifies root causes and enables targeted improvements rather than repeating defects. Budget success alone does not justify unchanged processes when quality degraded. Inspection-only approaches treat symptoms without fixing upstream causes. Public blame destroys psychological safety and hides systemic issues. Process optimization addresses root causes proactively.",
         "持續改善檢視成本與品質成果。經驗教訓與流程分析識別根本原因並促成針對性改善。僅預算成功不足以在品質下降時維持原流程。僅檢驗測試治標不治本。公開指責破壞心理安全。流程優化主動處理根本原因。",
         ["continuous-improvement", "process-optimization"]),
        ("An agile team on your {proj} program consistently delivers on commitment but cycle time for code review has increased forty percent over four sprints. What continuous improvement action is most appropriate?",
         "你 {proj_zh} 計畫的敏捷團隊持續達成承諾，但程式碼審查週期時間四個衝刺內增加百分之四十。最適當的持續改善行動是什麼？",
         [("Use retrospective data and metrics to identify bottlenecks in the review process and experiment with pair programming or review limits", "運用回顧數據與指標識別審查流程瓶頸，實驗配對程式設計或審查上限"),
          ("Ignore the trend because commitments are still met", "忽略趨勢，因承諾仍達成"),
          ("Eliminate code reviews to restore previous cycle times", "取消程式碼審查以恢復先前週期時間"),
          ("Add two more sprints to the release plan without addressing the bottleneck", "在不處理瓶頸下為發布計畫增加兩個衝刺")],
         0,
         "Continuous improvement monitors leading indicators, not just commitment delivery. Rising cycle time signals a growing bottleneck that will eventually affect throughput. Retrospective analysis with targeted experiments like pair programming addresses root causes. Ignoring trends allows problems to compound. Eliminating reviews sacrifices quality for speed. Adding sprints without fixing bottlenecks treats symptoms with schedule padding.",
         "持續改善監控領先指標，非僅承諾交付。週期時間上升表示瓶頸將最終影響產出。回顧分析與配對程式設計等實驗處理根本原因。忽略趨勢使問題惡化。取消審查以品質換速度。不修正瓶頸而加衝刺是以時程緩衝治標。",
         ["continuous-improvement", "kaizen"]),
        ("The PMO requests evidence of continuous improvement across your {ind} portfolio. Three projects use different methodologies. What should you provide?",
         "PMO 要求你的 {ind_zh} 組合持續改善證據。三個專案使用不同方法論。你應提供什麼？",
         [("A summary of improvement actions, metrics trends, and lessons learned from each project's retrospectives or phase reviews", "各專案回顧或階段審查的改善行動、指標趨勢與經驗教訓摘要"),
          ("A statement that agile projects improve automatically without documentation", "聲稱敏捷專案自動改善無需文件"),
          ("Only the project with the highest budget as a representative sample", "僅以最高預算專案作代表樣本"),
          ("A promise to implement improvement after all projects complete", "承諾所有專案完成後再實施改善")],
         0,
         "Continuous improvement evidence spans methodologies through documented actions, metric trends, and lessons learned from retrospectives or phase reviews. This demonstrates inspect-and-adapt across the portfolio. Claiming automatic improvement without evidence fails PMO accountability. Single-project sampling misrepresents portfolio performance. Deferring improvement until completion misses ongoing optimization opportunities. Kaizen requires visible, measured progress.",
         "持續改善證據跨方法論，來自文件化行動、指標趨勢與回顧或階段審查的經驗教訓，展現組合的檢視與調適。聲稱自動改善無證據無法滿足 PMO 問責。單一專案樣本誤代表組合績效。延至完成才改善錯失持續優化。Kaizen 需要可見、可衡量的進展。",
         ["continuous-improvement", "kaizen"]),
        ("Your {proj} team implemented a kaizen event that reduced deployment errors by sixty percent. Six months later, errors have returned to previous levels. What should you do?",
         "你的 {proj_zh} 團隊實施 Kaizen 活動將部署錯誤減少百分之六十。六個月後錯誤回到先前水準。你應怎麼做？",
         [("Investigate whether the improved process was standardized, training sustained, and metrics monitored, then re-establish controls", "調查改善流程是否標準化、培訓持續且指標受監控，然後重新建立控制"),
          ("Conduct another kaizen event identical to the first without analysis", "未經分析即進行與首次相同的 Kaizen 活動"),
          ("Conclude that kaizen does not work for this team", "斷定 Kaizen 對此團隊無效"),
          ("Accept the regression as normal variation", "接受退步為正常變異")],
         0,
         "Sustained improvement requires standardization, ongoing training, and metric monitoring after kaizen events. Investigating why gains eroded identifies whether process adherence or oversight failed. Repeating identical events without root cause analysis wastes effort. Dismissing kaizen ignores successful initial results. Accepting regression without investigation violates continuous improvement discipline. Process optimization must include sustainment mechanisms.",
         "持續改善需要 Kaizen 後的標準化、持續培訓與指標監控。調查成果流失原因可識別流程遵循或監督是否失敗。未分析即重複相同活動浪費努力。否定 Kaizen 忽略初期成功。未調查即接受退步違反持續改善紀律。",
         ["continuous-improvement", "kaizen"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 5) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be6_multi(idx):
    templates = [
        ("Your {ind} team wants to strengthen continuous improvement practices. Select TWO actions that support sustainable process optimization.",
         "你的 {ind_zh} 團隊希望強化持續改善實務。請選兩項支持永續流程優化的行動。",
         [("Establish measurable improvement goals reviewed at regular retrospectives or phase gates", "建立可衡量的改善目標並在定期回顧或階段關卡審查"),
          ("Document and standardize successful process changes so they persist beyond initial adoption", "文件化並標準化成功的流程變更以在初期採用後持續"),
          ("Limit improvement discussions to annual performance reviews only", "僅在年度績效評估討論改善"),
          ("Reward individual heroics that bypass established processes", "獎勵繞過既定流程的個人英雄主義"),
          ("Discontinue metrics tracking once initial targets are met", "達成初期目標後停止指標追蹤")],
         [0, 1],
         "Sustainable improvement requires measurable goals with regular review and standardization of successful changes. These practices embed kaizen into normal operations. Annual-only discussions are too infrequent for agile or fast-moving projects. Rewarding heroics that bypass process undermines standardization. Stopping metrics after initial success allows regression. Continuous improvement is an ongoing discipline, not a one-time event.",
         "永續改善需要可衡量目標與定期審查，以及標準化成功變更，將 Kaizen 嵌入日常營運。僅年度討論對快速專案太 infrequent。獎勵繞過流程的英雄主義 undermine 標準化。達標後停止指標允許退步。持續改善是持續紀律，非一次性活動。",
         ["continuous-improvement", "process-optimization"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 5) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be7_mcq(idx):
    templates = [
        ("Your company merges two divisions, and your project replaces both legacy CRM systems with one platform. Division A sales staff resist citing lost commission tracking; Division B staff are eager adopters. Leadership expects go-live in six months. What is the most effective approach?",
         "公司合併兩事業部，你的專案以單一平台取代兩套舊版 CRM。A 事業部業務以失去佣金追蹤抗拒；B 事業部積極採用。領導期望六個月內上線。最有效方法是什麼？",
         [("Develop a change impact assessment and targeted engagement plan addressing Division A's losses while leveraging Division B champions", "制定變革影響評估與針對性參與計畫，處理 A 事業部損失並善用 B 事業部 champion"),
          ("Mandate go-live on the original date with one generic training session", "按原定日期強制上線並提供一場通用培訓"),
          ("Delay until Division A voluntarily accepts the new system", "延後直到 A 事業部自願接受"),
          ("Deploy only to Division B and permanently exclude Division A", "先僅部署 B 事業部並永久排除 A")],
         0,
         "Organizational change requires understanding impacts and tailoring interventions. Impact assessment with targeted engagement addresses Division A's concerns while using Division B as a positive reference. Mandating go-live with generic training ignores resistance drivers. Waiting indefinitely misses leadership commitments. Excluding a division defeats the merger objective. Change management integrates stakeholder analysis, sponsorship, and phased readiness.",
         "組織變革需要了解影響並量身介入。影響評估與針對性參與處理 A 事業部顧慮並以 B 為正向參考。強制上線加通用培訓忽略抗拒原因。無限期等待錯失承諾。排除一事業部違背合併目標。組織變革管理整合利害關係人分析、贊助與分階段就緒。",
         ["organizational-change", "resistance"]),
        ("Your {ind} project introduces AI-assisted workflows that will change how analysts perform daily tasks. Middle managers express concern about team morale and skill obsolescence. What should you do first?",
         "你的 {ind_zh} 專案導入 AI 輔助工作流程，將改變分析師日常任務。中階經理擔心團隊士氣與技能過時。你應首先做什麼？",
         [("Engage managers in a change impact workshop to identify concerns, define reskilling paths, and co-create a communication plan", "讓經理參與變革影響工作坊，識別顧慮、定義再培訓路徑並共同制定溝通計畫"),
          ("Dismiss concerns because AI adoption is a strategic mandate", "因 AI 採用是策略命令而 dismiss 顧慮"),
          ("Announce the change via email without manager involvement", "未讓經理參與即以郵件宣布變革"),
          ("Delay the project until all managers approve enthusiastically", "延後專案直到所有經理熱情核准")],
         0,
         "Organizational change management addresses human impacts before technology rollout. Engaging managers in impact workshops builds ownership, identifies reskilling needs, and creates credible communication plans. Dismissing concerns increases resistance. Top-down email announcements without manager engagement undermine trust. Waiting for unanimous enthusiasm stalls strategic initiatives indefinitely. Middle managers are critical change agents who influence team adoption.",
         "組織變革管理在技術推廣前處理人的影響。讓經理參與影響工作坊建立主人翁意識、識別再培訓需求並制定可信溝通計畫。 dismiss 顧慮增加抗拒。未讓經理參與的自上而下郵件 undermine 信任。等待全員熱情同意會無限期阻礙策略計畫。中階經理是影響團隊採用的關鍵變革推動者。",
         ["organizational-change", "training"]),
        ("During {proj} rollout, post-training assessments show sixty percent of end users cannot complete core workflows independently. Go-live is two weeks away. What is the best action?",
         "在 {proj_zh} 推廣中，培訓後評估顯示百分之六十端使用者無法獨立完成核心工作流程。距上線兩週。最佳行動是什麼？",
         [("Recommend delaying go-live for targeted remedial training and report readiness metrics to the sponsor with a revised plan", "建議延後上線以進行針對性補救培訓，向贊助者報告就緒指標與修訂計畫"),
          ("Proceed with go-live and hope users learn on the job", "照常上線並希望使用者工作中學習"),
          ("Cancel all further training to save budget", "取消所有後續培訓以節省預算"),
          ("Blame users for not paying attention during training", "責怪使用者培訓時未專心")],
         0,
         "Readiness metrics should drive go/no-go decisions. Sixty percent failure on core workflows indicates the organization is not ready. Recommending delay with remedial training and sponsor reporting aligns with responsible change management. Proceeding hoping for on-the-job learning creates support chaos and adoption failure. Canceling training worsens readiness. Blaming users ignores training design and change management gaps. Organizational change requires demonstrated capability before cutover.",
         "就緒指標應驅動 go/no-go 決策。百分之六十無法完成核心流程表示組織未就緒。建議延後並補救培訓、向贊助者報告符合負責任的變革管理。照常上線指望工作中學習會造成支援混亂與採用失敗。取消培訓惡化就緒度。責怪使用者忽略培訓設計缺口。組織變革需在切換前展現能力。",
         ["organizational-change", "training"]),
        ("A {ind} culture assessment reveals strong silo mentality that undermines cross-functional collaboration needed for your program. Executive sponsors are committed but frontline resistance is high. What should you prioritize?",
         "在 {ind_zh} 文化評估顯示強烈 silo 心態， undermine 計畫所需的跨職能協作。高階贊助者 committed 但第一線抗拒高。你應優先什麼？",
         [("Work with sponsors to identify cross-functional change champions and create shared success metrics visible to all teams", "與贊助者合作識別跨職能變革 champion 並建立各團隊可見的共享成功指標"),
          ("Restructure the entire organization before continuing the project", "在繼續專案前重組整個組織"),
          ("Ignore cultural factors and focus only on technical delivery", "忽略文化因素僅專注技術交付"),
          ("Replace all resistant frontline staff immediately", "立即替換所有抗拒的第一線人員")],
         0,
         "Cultural change in programs requires sponsor-backed champions and shared metrics that incentivize collaboration over silo protection. This approach works within existing structures while shifting behaviors. Full reorganization exceeds project scope and timeline. Ignoring culture guarantees adoption failure regardless of technical success. Mass replacement is disruptive, legally risky, and does not address underlying cultural drivers. Change management addresses culture through influence and alignment.",
         "計畫中的文化變更需要贊助者支持的 champion 與共享指標，激勵協作而非 silo 保護。此法在現有結構內轉變行為。全面重組超出專案範圍與時程。忽略文化無論技術成功與否都會採用失敗。大規模替換具破壞性與法律風險。變革管理透過影響與對齊處理文化。",
         ["organizational-change", "culture"]),
        ("Your {proj} change network includes volunteer champions across five sites. Two sites show excellent adoption; three lag significantly despite identical training. What should you investigate first?",
         "你的 {proj_zh} 變革網路包含五個站點的志工 champion。兩站採用優異；三站儘管相同培訓仍明顯落後。你應首先調查什麼？",
         [("Local leadership engagement, champion effectiveness, and site-specific barriers through stakeholder interviews and adoption metrics", "透過利害關係人訪談與採用指標調查本地領導參與、champion 效能與站點特定障礙"),
          ("Replace all training materials with new versions", "以更換全新培訓教材"),
          ("Assume the lagging sites have less capable employees", "假設落後站點員工能力較差"),
          ("Withdraw champions from successful sites to force equal attention", "從成功站點撤回 champion 以強制均等關注")],
         0,
         "Uneven adoption with identical training suggests local contextual factors, not material deficiencies. Investigating leadership engagement, champion effectiveness, and site-specific barriers identifies targeted interventions. Replacing materials without diagnosis wastes effort. Assuming employee capability differences is biased and unproductive. Withdrawing successful champions penalizes high performers without fixing lagging sites. Change management requires localized diagnosis.",
         "相同培訓下採用不均表示本地情境因素，非教材不足。調查領導參與、champion 效能與站點障礙可識別針對性介入。未診斷即換教材浪費努力。假設員工能力差有偏見且無效。撤回成功 champion 懲罰高績效者而未修正落後站點。變革管理需要本地化診斷。",
         ["organizational-change", "adoption"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 6) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be7_multi(idx):
    templates = [
        ("Your agile team adopts a new CI/CD pipeline changing how developers deploy code. Several senior developers are skeptical. Select TWO actions that best support organizational change.",
         "敏捷團隊採用改變開發者部署方式的新 CI/CD 管線。幾位資深開發者持懷疑態度。請選兩項最支持組織變革的行動。",
         [("Involve skeptical developers early in pilot design and incorporate their feedback into rollout plans", "讓持懷疑開發者早期參與試點設計並將回饋納入推廣計畫"),
          ("Identify and empower team members who successfully adopt the pipeline to mentor others", "找出成功採用管線的成員並授權其指導他人"),
          ("Mandate immediate full adoption and remove legacy deployment access on day one", "第一天強制全面採用並移除舊版部署存取"),
          ("Exclude skeptical developers from pipeline decisions to avoid delays", "排除持懷疑開發者參與管線決策以避免延遲"),
          ("Postpone the change until every developer voluntarily agrees", "延後變革直到每位開發者自願同意")],
         [0, 1],
         "Organizational change succeeds through participation and peer influence. Involving skeptics in pilot design converts resistance into ownership. Empowering early adopters as mentors leverages social proof. Day-one mandates without support create fear and workarounds. Excluding skeptics reinforces opposition. Waiting for unanimous agreement stalls improvement indefinitely. Agile change management favors incremental adoption with coaching.",
         "組織變革透過參與與同儕影響成功。讓懷疑者參與試點設計將抗拒轉為主人翁意識。授權早期採用者擔任導師運用社會證明。第一天強制切換無支援會產生恐懼與變通。排除懷疑者強化對立。等待全員同意會無限期阻礙。敏捷變革管理偏好漸進採用與輔導。",
         ["organizational-change", "adoption"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 6) % len(INDUSTRIES)]
    stem_en, stem_zh = t[0], t[1]
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

def get_be8_mcq(idx):
    templates = [
        ("Midway through a {ind} construction project, the government announces new environmental inspection requirements adding four weeks to approval. The contract is firm fixed-price with late penalties. What should you do first?",
         "營造 {ind_zh} 專案進行到一半，政府宣布新環境檢查要求使核准增加四週。合約為固定總價且延遲有罰則。你應首先做什麼？",
         [("Analyze the external change impact on schedule and cost, then engage the sponsor and contract administrator about contract adjustments or claims", "分析外部變更對時程與成本的影響，與贊助者及合約管理員討論合約調整或求償"),
          ("Absorb the delay internally without informing the client", "內部吸收延遲且不告知客戶"),
          ("Immediately terminate the contract citing force majeure", "立即以不可抗力終止合約"),
          ("Accelerate all remaining activities without revising the baseline", "不修訂基線即加速所有剩餘活動")],
         0,
         "External regulatory changes may qualify as contract-level events requiring formal impact assessment. Analyzing schedule and cost impact provides factual basis for sponsor and legal discussions about claims or change orders. Hiding delay violates transparency and notification clauses. Terminating without analysis is premature. Blind crashing increases cost and safety risk without addressing the approval bottleneck. PESTLE factors require formal assessment and stakeholder alignment.",
         "外部法規變更可能構成合約層級事件，需正式影響評估。分析時程與成本影響為求償或變更令討論提供事實基礎。隱瞞延遲違反透明與通知條款。未分析即終止過早。盲目趕工增加成本與安全風險。PESTLE 因素需正式評估與利害關係人對齊。",
         ["external-environment", "regulatory"]),
        ("Your organization's {proj} strategy assumes stable interest rates. Central bank announcements indicate likely rate increases affecting project financing costs by fifteen percent. What should you do first?",
         "組織 {proj_zh} 策略假設利率穩定。央行宣布可能升息，使專案融資成本增加百分之十五。你應首先做什麼？",
         [("Update the financial analysis with revised rate assumptions and present impact options to the sponsor and portfolio board", "以修訂利率假設更新財務分析，向贊助者與組合委員會呈現影響選項"),
          ("Ignore the announcement until rates actually change", "在利率實際變動前忽略宣布"),
          ("Cancel the project immediately without financial modeling", "未做財務建模即立即取消專案"),
          ("Continue without informing stakeholders to avoid panic", "不告知利害關係人以避免恐慌而繼續")],
         0,
         "External economic factors in PESTLE analysis require monitoring and proactive reassessment. Updating financial models with revised assumptions and presenting options enables informed sponsor and portfolio decisions. Ignoring signals until changes occur removes lead time for mitigation. Canceling without analysis is reactive and may discard viable options. Withholding information violates stakeholder trust and governance transparency. Market shifts demand updated business case evaluation.",
         "PESTLE 分析中的外部經濟因素需要監控與主動重評。以修訂假設更新財務模型並呈現選項支持知情決策。忽略訊號直到變動發生會失去緩解時間。未分析即取消是被動的且可能放棄可行選項。隱瞞資訊違反信任與治理透明。市場轉變需要更新商業案例評估。",
         ["external-environment", "market-shifts"]),
        ("The board mandates ESG reporting for all {ind} projects starting next quarter. Your project is sixty percent complete with no sustainability metrics tracked. What is the best immediate action?",
         "董事會要求下季起所有 {ind_zh} 專案 ESG 報告。你的專案完成百分之六十且未追蹤永續指標。最佳立即行動是什麼？",
         [("Assess applicable ESG requirements, identify data gaps, and integrate sustainability metrics into remaining deliverables and reporting", "評估適用 ESG 要求、識別數據缺口，將永續指標整合至剩餘交付物與報告"),
          ("Wait until project closure to address ESG retroactively", "等到專案結束再 retroactive 處理 ESG"),
          ("Claim the mandate does not apply because the project started earlier", "主張專案較早開始故命令不適用"),
          ("Outsource all ESG reporting to a consultant without internal integration", "將所有 ESG 報告外包給顧問而不內部整合")],
         0,
         "ESG mandates are external governance requirements affecting project reporting regardless of start date. Assessing requirements, identifying gaps, and integrating metrics into remaining work ensures compliance with board expectations. Deferring to closure may miss data collection windows. Claiming exemption without legal review is risky. Consultant outsourcing without internal integration produces reports disconnected from project reality. Sustainability requirements are integrated into project management, not added cosmetically at the end.",
         "ESG 命令是影響專案報告的外部治理要求，不論開始日期。評估要求、識別缺口並整合至剩餘工作可符合董事會期望。延至結束可能錯失數據收集窗口。未經法律審查主張豁免有風險。無內部整合的外包報告與專案現實脫節。永續要求整合於專案管理，非結尾表面添加。",
         ["external-environment", "ESG"]),
        ("A competitor launches an AI-powered {ind} product six months ahead of your planned release. The sponsor asks whether to accelerate your timeline. What should you provide first?",
         "競爭對手比你計畫上市早六個月推出 AI 驅動的 {ind_zh} 產品。贊助者詢問是否加速時程。你應首先提供什麼？",
         [("An impact analysis comparing accelerated delivery trade-offs against quality, compliance, and market differentiation risks", "比較加速交付取捨與品質、合規及市場差異化風險的影響分析"),
          ("Immediate agreement to accelerate without team consultation", "未諮詢團隊即立即同意加速"),
          ("A recommendation to cancel because the competitor won", "因競爭對手已贏而建議取消"),
          ("Assurance that the original timeline is optimal without analysis", "未經分析即保證原時程最優")],
         0,
         "External competitive pressure requires structured analysis, not reactive decisions. Impact analysis comparing acceleration trade-offs against quality, compliance, and differentiation helps sponsors make informed choices. Immediate acceleration without consultation ignores feasibility and risk. Canceling assumes the competitor's timing defines market success permanently. Unsubstantiated timeline assurances fail governance standards. AI and market shifts demand evidence-based schedule recommendations.",
         "外部競爭壓力需要結構化分析，非 reactive 決策。比較加速取捨與品質、合規及差異化的影響分析支持知情選擇。未諮詢即加速忽略可行性與風險。取消假設競爭對手時程永久定義市場成功。未經證明的時程保證不符治理標準。AI 與市場轉變需要循證時程建議。",
         ["external-environment", "AI"]),
        ("Your {proj} depends on a cloud provider operating in a region facing new data sovereignty laws requiring local data residency. Migration is seventy percent complete. What should you do first?",
         "你的 {proj_zh} 依賴營運於面臨新資料主權法、要求本地資料 residency 的區域之雲端供應商。遷移完成百分之七十。你應首先做什麼？",
         [("Conduct a PESTLE/legal impact assessment with compliance and architecture teams to determine required infrastructure changes and timeline impact", "與合規及架構團隊進行 PESTLE/法律影響評估，決定所需基礎設施變更與時程影響"),
          ("Complete migration as planned and address sovereignty after go-live", "按計畫完成遷移，上線後再處理主權"),
          ("Ignore the new laws because the provider has not notified you", "因供應商未通知而忽略新法"),
          ("Immediately revert all migrated workloads to on-premises", "立即將所有已遷移工作負載 revert 至地端")],
         0,
         "Data sovereignty laws are external legal factors requiring immediate assessment even mid-migration. PESTLE/legal impact analysis with compliance and architecture teams determines required changes and schedule implications before committing further work. Completing migration without compliance creates regulatory exposure. Ignoring laws because the provider is silent is negligent—the organization remains accountable. Immediate full revert may be unnecessary and costly without analysis. External regulatory changes demand structured assessment.",
         "資料主權法是外部法律因素，即使遷移中期也需立即評估。PESTLE/法律影響分析與合規及架構團隊決定所需變更與時程影響。不合規完成遷移造成監管暴露。因供應商未通知而忽略法律是疏忽——組織仍須負責。未分析即全面 revert 可能不必要且 costly。外部法規變更需要結構化評估。",
         ["external-environment", "PESTLE"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 7) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems(t, ind), idx)
    opts, corr = _rotate(t[2], t[3], idx // len(templates))
    return q(stem_en, stem_zh, opts, corr, t[4], t[5], t[6])

def get_be8_multi(idx):
    templates = [
        ("A predictive {ind} project sources critical components from a region experiencing geopolitical instability. Select TWO actions to address external environment risks.",
         "預測式 {ind_zh} 專案從地緣政治不穩定區域採購關鍵元件。請選兩項應對外部環境風險的行動。",
         [("Develop alternative sourcing options and document them in the risk register with assigned owners", "發展替代採購方案並在風險登記冊記錄並指定負責人"),
          ("Increase inventory buffer or secure advance purchase agreements for long-lead components", "增加庫存緩衝或為長交期元件簽訂預購協議"),
          ("Ignore geopolitical news because the contract penalizes the supplier for late delivery", "忽略地緣政治新聞，因合約對供應商延遲有罰則"),
          ("Reduce project scope to eliminate all externally sourced components", "縮減範圍以消除所有外部採購元件"),
          ("Wait until a supply disruption occurs before taking any action", "等到供應中斷發生後才採取行動")],
         [0, 1],
         "External environment risks require proactive mitigation. Alternative sourcing with documented owners provides fallback if the primary supplier becomes unavailable. Inventory buffers or advance purchase agreements protect against delays beyond contractual penalties. Ignoring geopolitical signals is reactive—penalties cannot restore lost time. Eliminating all external components is usually infeasible. Waiting converts manageable risk into certain issue.",
         "外部環境風險需主動緩解。有負責人的替代採購在主要供應商不可用時提供備援。庫存緩衝或預購協議防範合約罰則無法挽回的延遲。忽略地緣政治訊號是被動的——罰則無法恢復失去的時間。消除所有外部元件通常不可行。等待會把可管理風險變成確定問題。",
         ["external-environment", "supply-chain"]),
    ]
    t = templates[idx % len(templates)]
    ind = INDUSTRIES[(idx + 7) % len(INDUSTRIES)]
    stem_en, stem_zh = _add_variant(*_stems_ind_only(t, ind), idx)
    shift = idx % 3
    opts_raw = t[2]
    n = len(opts_raw)
    rotated = [opts_raw[(i + shift) % n] for i in range(n)]
    correct = sorted([(c - shift) % n for c in t[3]])
    opts = [opt(e, z) for e, z in rotated]
    return q(stem_en, stem_zh, opts, correct, t[4], t[5], t[6])

MCQ_GETTERS = {
    "BE1": get_be1_mcq,
    "BE2": get_be2_mcq,
    "BE3": get_be3_mcq,
    "BE4": get_be4_mcq,
    "BE5": get_be5_mcq,
    "BE6": get_be6_mcq,
    "BE7": get_be7_mcq,
    "BE8": get_be8_mcq,
}

MULTI_GETTERS = {
    "BE1": get_be1_multi,
    "BE2": get_be2_multi,
    "BE3": get_be3_multi,
    "BE4": get_be4_multi,
    "BE5": get_be5_multi,
    "BE6": get_be6_multi,
    "BE7": get_be7_multi,
    "BE8": get_be8_multi,
}
