import { EXAM } from './examConstants'
import type { AttemptRecord, AnswerRecord, DailyRecord } from '@/db/index'

export interface StatsOverview {
  totalAttempts: number
  totalAnswered: number
  avgScore: number
  bestScore: number
  currentStreak: number
  bestStreak: number
  coveragePct: number
  masteredPct: number
}

export interface ScoreTrendPoint {
  date: string
  score: number
  mode: string
}

export interface DomainRadarPoint {
  domain: string
  latest: number
  best: number
  target: number
}

export interface TaskHeatmapPoint {
  task: string
  accuracy: number
  total: number
}

export interface ReadinessResult {
  label: string
  hint: string
}

function pct(correct: number, total: number): number {
  return total === 0 ? 0 : (correct / total) * 100
}

function normalizeQuestionId(id: string): string {
  return id.replace(/__dup\d+$/, '').replace(/__fill\d+$/, '')
}

function computeStreakFromDaily(daily: DailyRecord[]): { current: number; best: number } {
  if (daily.length === 0) return { current: 0, best: 0 }

  const activeDays = daily
    .filter((d) => d.answered > 0)
    .sort((a, b) => a.date.localeCompare(b.date))

  if (activeDays.length === 0) return { current: 0, best: 0 }

  const bestFromRecords = Math.max(...activeDays.map((d) => d.streakDay), 0)

  const dateSet = new Set(activeDays.map((d) => d.date))
  let current = 0
  const cursor = new Date()

  for (let i = 0; i < 400; i += 1) {
    const key = cursor.toISOString().slice(0, 10)
    if (dateSet.has(key)) {
      current += 1
      cursor.setDate(cursor.getDate() - 1)
    } else if (current === 0) {
      cursor.setDate(cursor.getDate() - 1)
      if (i > 1) break
    } else {
      break
    }
  }

  const latestStreak = activeDays[activeDays.length - 1]?.streakDay ?? 0
  return {
    current: Math.max(current, latestStreak),
    best: Math.max(bestFromRecords, current),
  }
}

export function computeOverview(
  attempts: AttemptRecord[],
  daily: DailyRecord[],
  bankTotal: number,
  allAnswers?: AnswerRecord[],
): StatsOverview {
  const completed = attempts.filter(
    (a) => a.status === 'completed' || a.status === 'quit',
  )
  const scored = completed.filter((a) => a.score != null)

  const totalAttempts = completed.length
  const scores = scored.map((a) => a.score!.pct)
  const avgScore = scores.length === 0 ? 0 : scores.reduce((s, v) => s + v, 0) / scores.length
  const bestScore = scores.length === 0 ? 0 : Math.max(...scores)

  const totalAnswered =
    allAnswers?.length ??
    scored.reduce((sum, a) => sum + (a.score?.max ?? 0), 0)

  const { current: currentStreak, best: bestStreak } = computeStreakFromDaily(daily)

  let seenCount = 0
  let masteredCount = 0

  if (allAnswers && allAnswers.length > 0) {
    const byQuestion = new Map<string, { correct: number; total: number }>()
    for (const ans of allAnswers) {
      const qid = normalizeQuestionId(ans.questionId)
      const bucket = byQuestion.get(qid) ?? { correct: 0, total: 0 }
      bucket.total += 1
      if (ans.correct) bucket.correct += 1
      byQuestion.set(qid, bucket)
    }
    seenCount = byQuestion.size
    masteredCount = [...byQuestion.values()].filter(
      (s) => s.total >= 1 && pct(s.correct, s.total) >= 75,
    ).length
  }

  const coveragePct = bankTotal === 0 ? 0 : (seenCount / bankTotal) * 100
  const masteredPct = seenCount === 0 ? 0 : (masteredCount / seenCount) * 100

  return {
    totalAttempts,
    totalAnswered,
    avgScore,
    bestScore,
    currentStreak,
    bestStreak,
    coveragePct,
    masteredPct,
  }
}

export function computeScoreTrend(attempts: AttemptRecord[]): ScoreTrendPoint[] {
  return attempts
    .filter((a) => a.score != null && a.finishedAt != null)
    .sort((a, b) => (a.finishedAt ?? 0) - (b.finishedAt ?? 0))
    .map((a) => ({
      date: new Date(a.finishedAt!).toISOString().slice(0, 10),
      score: Math.round(a.score!.pct),
      mode: a.mode,
    }))
}

function domainPct(
  attempt: AttemptRecord | null | undefined,
  domain: string,
): number {
  if (!attempt?.score?.byDomain[domain]) return 0
  const { correct, total } = attempt.score.byDomain[domain]
  return pct(correct, total)
}

export function computeDomainRadar(
  latestAttempt: AttemptRecord | null,
  bestAttempt: AttemptRecord | null,
): DomainRadarPoint[] {
  const domains = ['people', 'process', 'business'] as const
  return domains.map((domain) => ({
    domain,
    latest: Math.round(domainPct(latestAttempt, domain)),
    best: Math.round(domainPct(bestAttempt, domain)),
    target: EXAM.PASS_PROXY_PCT,
  }))
}

export function computeTaskHeatmap(
  answers: AnswerRecord[],
  taskByQuestionId: Record<string, string>,
): TaskHeatmapPoint[] {
  const buckets = new Map<string, { correct: number; total: number }>()

  for (const ans of answers) {
    const qid = normalizeQuestionId(ans.questionId)
    const task = taskByQuestionId[qid]
    if (!task) continue
    const bucket = buckets.get(task) ?? { correct: 0, total: 0 }
    bucket.total += 1
    if (ans.correct) bucket.correct += 1
    buckets.set(task, bucket)
  }

  return [...buckets.entries()]
    .map(([task, stats]) => ({
      task,
      accuracy: pct(stats.correct, stats.total),
      total: stats.total,
    }))
    .sort((a, b) => a.task.localeCompare(b.task))
}

export function computeReadiness(
  overview: StatsOverview,
  domainScores: Record<string, number>,
): ReadinessResult {
  const domainEntries = Object.entries(domainScores)
  const weakest = domainEntries.sort((a, b) => a[1] - b[1])[0]

  if (overview.avgScore >= EXAM.PASS_PROXY_PCT && overview.coveragePct >= 50) {
    if (weakest && weakest[1] < EXAM.PASS_PROXY_PCT) {
      return {
        label: 'pushDomain',
        hint: weakest[0],
      }
    }
    return { label: 'onTrack', hint: '' }
  }

  if (overview.avgScore >= EXAM.BAND_THRESHOLDS.belowTarget) {
    return { label: 'keepGoing', hint: '' }
  }

  if (weakest) {
    return { label: 'pushDomain', hint: weakest[0] }
  }

  return { label: 'keepGoing', hint: '' }
}

export function findBestAttempt(attempts: AttemptRecord[]): AttemptRecord | null {
  const scored = attempts.filter((a) => a.score != null)
  if (scored.length === 0) return null
  return scored.reduce((best, a) =>
    (a.score!.pct > best.score!.pct ? a : best),
  )
}

export function findLatestAttempt(attempts: AttemptRecord[]): AttemptRecord | null {
  const scored = attempts.filter((a) => a.finishedAt != null && a.score != null)
  if (scored.length === 0) return null
  return scored.sort((a, b) => (b.finishedAt ?? 0) - (a.finishedAt ?? 0))[0]
}

export function buildDailyFromAnswers(answers: AnswerRecord[]): DailyRecord[] {
  const byDate = new Map<string, { answered: number; correct: number; minutes: number }>()

  for (const ans of answers) {
    const date = new Date(ans.answeredAt).toISOString().slice(0, 10)
    const bucket = byDate.get(date) ?? { answered: 0, correct: 0, minutes: 0 }
    bucket.answered += 1
    if (ans.correct) bucket.correct += 1
    bucket.minutes += ans.timeSec / 60
    byDate.set(date, bucket)
  }

  const sortedDates = [...byDate.keys()].sort()
  const records: DailyRecord[] = []
  let streak = 0
  let prevDate: string | null = null

  for (const date of sortedDates) {
    const stats = byDate.get(date)!
    if (prevDate) {
      const prev = new Date(prevDate)
      const curr = new Date(date)
      const diffDays = Math.round((curr.getTime() - prev.getTime()) / 86400000)
      streak = diffDays === 1 ? streak + 1 : 1
    } else {
      streak = 1
    }
    prevDate = date
    records.push({
      date,
      answered: stats.answered,
      correctPct: pct(stats.correct, stats.answered),
      minutes: Math.round(stats.minutes),
      streakDay: streak,
    })
  }

  return records
}
