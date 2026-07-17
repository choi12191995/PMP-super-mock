import { EXAM } from '../examConstants'
import type {
  AnswerGiven,
  Band,
  Question,
  ScoreResult,
} from '../types'

function arraysEqualSorted(a: readonly string[], b: readonly string[]): boolean {
  if (a.length !== b.length) return false
  const sa = [...a].sort()
  const sb = [...b].sort()
  return sa.every((value, index) => value === sb[index])
}

function numberArraysEqualSorted(a: readonly number[], b: readonly number[]): boolean {
  if (a.length !== b.length) return false
  const sa = [...a].sort((x, y) => x - y)
  const sb = [...b].sort((x, y) => x - y)
  return sa.every((value, index) => value === sb[index])
}

export function isAnswerCorrect(question: Question, given: unknown): boolean {
  switch (question.type) {
    case 'mcq':
    case 'graphic-mcq':
      return typeof given === 'number' && given === question.correct
    case 'multi':
      return (
        Array.isArray(given) &&
        given.every((value) => typeof value === 'number') &&
        numberArraysEqualSorted(given as number[], question.correct)
      )
    case 'matching':
    case 'enhanced-matching':
      return (
        Array.isArray(given) &&
        given.every((value) => typeof value === 'number') &&
        given.length === question.correct.length &&
        (given as number[]).every((value, index) => value === question.correct[index])
      )
    case 'hotspot':
      return (
        Array.isArray(given) &&
        given.every((value) => typeof value === 'string') &&
        arraysEqualSorted(given as string[], question.correct)
      )
    case 'pulldown': {
      if (typeof given !== 'object' || given === null) return false
      const selections = given as Record<string, unknown>
      return question.blanks.every((blank) => selections[blank.id] === blank.correct)
    }
    default: {
      const _exhaustive: never = question
      return _exhaustive
    }
  }
}

function incrementBucket(
  buckets: Record<string, { correct: number; total: number }>,
  key: string,
  correct: boolean,
): void {
  const bucket = buckets[key] ?? { correct: 0, total: 0 }
  bucket.total += 1
  if (correct) bucket.correct += 1
  buckets[key] = bucket
}

export function computeScore(
  questions: Question[],
  answers: Map<string, AnswerGiven>,
): ScoreResult {
  let raw = 0
  const max = questions.length
  const byDomain: ScoreResult['byDomain'] = {}
  const byTask: ScoreResult['byTask'] = {}
  const byType: ScoreResult['byType'] = {}
  const byApproach: ScoreResult['byApproach'] = {}

  for (const question of questions) {
    const answer = answers.get(question.id)
    const correct = answer?.correct ?? false
    if (correct) raw += 1

    incrementBucket(byDomain, question.domain, correct)
    incrementBucket(byTask, question.task, correct)
    incrementBucket(byType, question.type, correct)
    incrementBucket(byApproach, question.approach, correct)
  }

  const pct = max === 0 ? 0 : (raw / max) * 100

  return { raw, max, pct, byDomain, byTask, byType, byApproach }
}

export function computeBand(pct: number): Band {
  if (pct >= EXAM.BAND_THRESHOLDS.aboveTarget) return 'AT'
  if (pct >= EXAM.BAND_THRESHOLDS.target) return 'T'
  if (pct >= EXAM.BAND_THRESHOLDS.belowTarget) return 'BT'
  return 'NI'
}

export function computeDomainBands(
  byDomain: Record<string, { correct: number; total: number }>,
): Record<string, Band> {
  const bands: Record<string, Band> = {}
  for (const [domain, stats] of Object.entries(byDomain)) {
    const pct = stats.total === 0 ? 0 : (stats.correct / stats.total) * 100
    bands[domain] = computeBand(pct)
  }
  return bands
}
