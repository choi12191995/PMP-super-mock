/**
 * All exam-fact constants in one place. Constants with ASSUMPTION=true
 * are unofficial estimates — update when PMI publishes official numbers.
 */

export const EXAM = {
  TOTAL_QUESTIONS: 180,
  SCORED_QUESTIONS: 170,
  PRETEST_QUESTIONS: 10,
  DURATION_MINUTES: 240,
  PACE_SECONDS: 80,

  SECTION_A_CASES: 5,
  SECTION_A_QUESTIONS_PER_CASE: 4,
  /** @ASSUMPTION PMI has not published section sizes */
  SECTION_A_TOTAL: 20,
  /** @ASSUMPTION */
  SECTION_B_TOTAL: 80,
  /** @ASSUMPTION */
  SECTION_C_TOTAL: 80,

  BREAK_DURATION_MINUTES: 10,
  BREAK_COUNT: 2,

  DOMAIN_WEIGHTS: {
    people: 0.33,
    process: 0.41,
    business: 0.26,
  } as const,

  PASS_PROXY_PCT: 65,

  BAND_THRESHOLDS: {
    aboveTarget: 75,
    target: 65,
    belowTarget: 50,
  } as const,

  APPROACH_MIX: {
    predictive: 0.4,
    agile: 0.3,
    hybrid: 0.3,
  } as const,

  DIFFICULTY_MIX: {
    1: 0.25,
    2: 0.5,
    3: 0.25,
  } as const,
} as const

export const BANK_TARGETS = {
  total: 1800,
  people: 594,
  process: 738,
  business: 468,
  tolerance: 0.02,

  types: {
    mcq: 1170,
    multi: 216,
    case: 144,
    'graphic-mcq': 90,
    matching: 54,
    'enhanced-matching': 36,
    hotspot: 45,
    pulldown: 45,
  },

  approach: {
    predictive: 720,
    agile: 540,
    hybrid: 540,
  },

  difficulty: {
    1: 450,
    2: 900,
    3: 450,
  },
} as const

export const ECO_TASKS = {
  people: [
    { id: 'PPL1', name: 'Develop a common vision' },
    { id: 'PPL2', name: 'Manage conflicts' },
    { id: 'PPL3', name: 'Lead the project team' },
    { id: 'PPL4', name: 'Engage stakeholders' },
    { id: 'PPL5', name: 'Align stakeholder expectations' },
    { id: 'PPL6', name: 'Manage stakeholder expectations' },
    { id: 'PPL7', name: 'Ensure knowledge transfer' },
    { id: 'PPL8', name: 'Plan and manage communication' },
  ],
  process: [
    { id: 'PRC1', name: 'Integrated PM plan & delivery' },
    { id: 'PRC2', name: 'Scope' },
    { id: 'PRC3', name: 'Value-based delivery' },
    { id: 'PRC4', name: 'Resources' },
    { id: 'PRC5', name: 'Procurement' },
    { id: 'PRC6', name: 'Finance' },
    { id: 'PRC7', name: 'Quality' },
    { id: 'PRC8', name: 'Schedule' },
    { id: 'PRC9', name: 'Evaluate project status' },
    { id: 'PRC10', name: 'Closure' },
  ],
  business: [
    { id: 'BE1', name: 'Governance' },
    { id: 'BE2', name: 'Compliance' },
    { id: 'BE3', name: 'Manage & control changes' },
    { id: 'BE4', name: 'Impediments & issues' },
    { id: 'BE5', name: 'Risk' },
    { id: 'BE6', name: 'Continuous improvement' },
    { id: 'BE7', name: 'Organizational change' },
    { id: 'BE8', name: 'External environment changes' },
  ],
} as const
