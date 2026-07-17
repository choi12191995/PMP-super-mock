import Dexie, { type EntityTable } from 'dexie'

export interface AttemptRecord {
  id: string
  mode: string
  startedAt: number
  finishedAt: number | null
  durationSec: number
  config: Record<string, unknown>
  score: {
    raw: number
    max: number
    pct: number
    byDomain: Record<string, { correct: number; total: number }>
    byTask: Record<string, { correct: number; total: number }>
    byType: Record<string, { correct: number; total: number }>
    byApproach: Record<string, { correct: number; total: number }>
  } | null
  band: 'AT' | 'T' | 'BT' | 'NI' | null
  passedProxy: boolean | null
  status: 'in-progress' | 'completed' | 'quit'
  aiSummary?: string | null
}

export interface AnswerRecord {
  id: string
  attemptId: string
  questionId: string
  given: unknown
  correct: boolean
  timeSec: number
  flagged: boolean
  changedCount: number
  answeredAt: number
}

export interface SrsRecord {
  questionId: string
  wrongCount: number
  lastWrongAt: number
  due: number
  interval: number
  ease: number
}

export interface DailyRecord {
  date: string
  answered: number
  correctPct: number
  minutes: number
  streakDay: number
}

const db = new Dexie('pmp-super-mock') as Dexie & {
  attempts: EntityTable<AttemptRecord, 'id'>
  answers: EntityTable<AnswerRecord, 'id'>
  srs: EntityTable<SrsRecord, 'questionId'>
  daily: EntityTable<DailyRecord, 'date'>
}

db.version(1).stores({
  attempts: 'id, mode, startedAt, status',
  answers: 'id, attemptId, questionId',
  srs: 'questionId, due',
  daily: 'date',
})

export { db }
