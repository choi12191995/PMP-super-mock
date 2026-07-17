export interface LText {
  en: string
  zh: string
}

export type Domain = 'people' | 'process' | 'business'
export type Approach = 'predictive' | 'agile' | 'hybrid'
export type Difficulty = 1 | 2 | 3
export type QType =
  | 'mcq'
  | 'multi'
  | 'matching'
  | 'enhanced-matching'
  | 'hotspot'
  | 'pulldown'
  | 'graphic-mcq'

export interface QuestionBase {
  id: string
  type: QType
  domain: Domain
  task: string
  approach: Approach
  difficulty: Difficulty
  stem: LText
  explanation: LText
  refs?: string[]
  media?: string
  tags?: string[]
  caseId?: string
}

export interface McqQ extends QuestionBase {
  type: 'mcq' | 'graphic-mcq'
  options: LText[]
  correct: number
}

export interface MultiQ extends QuestionBase {
  type: 'multi'
  options: LText[]
  correct: number[]
  selectN: number
}

export interface MatchingQ extends QuestionBase {
  type: 'matching' | 'enhanced-matching'
  left: LText[]
  right: LText[]
  correct: number[]
}

export interface HotspotQ extends QuestionBase {
  type: 'hotspot'
  media: string
  regions: { id: string; label: LText }[]
  correct: string[]
}

export interface PulldownQ extends QuestionBase {
  type: 'pulldown'
  blanks: { id: string; options: LText[]; correct: number }[]
}

export type Question = McqQ | MultiQ | MatchingQ | HotspotQ | PulldownQ

export interface CaseSet {
  id: string
  scenario: LText
  media?: string
  questionIds: string[]
}

export interface BankManifest {
  version: string
  counts: {
    total: number
    people: number
    process: number
    business: number
  }
  chunks: {
    file: string
    domain: Domain
    count: number
    hash: string
  }[]
  cases: {
    file: string
    count: number
  }[]
}

export interface ExamConfig {
  mode: 'real' | 'full-untimed' | 'free' | 'custom'
  questionCount: number
  timerMode: 'off' | 'count-up' | 'countdown'
  timerSeconds?: number
  feedbackMode: 'end' | 'immediate'
  filters: {
    domains?: Domain[]
    tasks?: string[]
    approaches?: Approach[]
    difficulties?: Difficulty[]
    types?: QType[]
    wrongOnly?: boolean
  }
  onvue: boolean
  aiChat: boolean
  seed?: number
}

export interface ScoreResult {
  raw: number
  max: number
  pct: number
  byDomain: Record<string, { correct: number; total: number }>
  byTask: Record<string, { correct: number; total: number }>
  byType: Record<string, { correct: number; total: number }>
  byApproach: Record<string, { correct: number; total: number }>
}

export type Band = 'AT' | 'T' | 'BT' | 'NI'

export interface AnswerGiven {
  questionId: string
  given: unknown
  correct: boolean
  timeSec: number
  flagged: boolean
  changedCount: number
}
