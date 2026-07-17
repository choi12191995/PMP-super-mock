import { EXAM } from './examConstants'
import type { AttemptRecord, AnswerRecord, DailyRecord } from '@/db/index'

export type BadgeId = 'first180' | 'streak7' | 'businessPro' | 'nightOwl' | 'perfectDomain'

export interface Badge {
  id: BadgeId
  earned: boolean
  earnedAt?: number
}

function normalizeQuestionId(id: string): string {
  return id.replace(/__dup\d+$/, '').replace(/__fill\d+$/, '')
}

export function computeBadges(
  attempts: AttemptRecord[],
  answers: AnswerRecord[],
  daily: DailyRecord[],
): Badge[] {
  const completed = attempts.filter((a) => a.status === 'completed')
  const scored = completed.filter((a) => a.score != null)

  const first180 = scored.some((a) => (a.score?.max ?? 0) >= EXAM.TOTAL_QUESTIONS)
  const first180At = scored.find((a) => (a.score?.max ?? 0) >= EXAM.TOTAL_QUESTIONS)?.finishedAt

  const bestStreak = daily.length
    ? Math.max(...daily.map((d) => d.streakDay), 0)
    : 0
  const streak7 = bestStreak >= 7

  const latestWithDomain = [...scored]
    .sort((a, b) => (b.finishedAt ?? 0) - (a.finishedAt ?? 0))
    .find((a) => a.score?.byDomain.business)
  const businessPct = latestWithDomain?.score?.byDomain.business
  const businessPro =
    businessPct != null &&
    businessPct.total > 0 &&
    (businessPct.correct / businessPct.total) * 100 >= EXAM.PASS_PROXY_PCT

  const nightOwl = answers.some((a) => {
    const hour = new Date(a.answeredAt).getHours()
    return hour >= 22 || hour < 5
  })

  const perfectDomain = scored.some((a) => {
    if (!a.score?.byDomain) return false
    return Object.values(a.score.byDomain).some(
      (d) => d.total >= 10 && d.correct === d.total,
    )
  })

  return [
    { id: 'first180', earned: first180, earnedAt: first180At ?? undefined },
    { id: 'streak7', earned: streak7 },
    { id: 'businessPro', earned: businessPro },
    { id: 'nightOwl', earned: nightOwl },
    { id: 'perfectDomain', earned: perfectDomain },
  ]
}

export function countSeenQuestions(answers: AnswerRecord[]): number {
  const seen = new Set<string>()
  for (const a of answers) {
    seen.add(normalizeQuestionId(a.questionId))
  }
  return seen.size
}
