import { db, type SrsRecord } from '@/db/index'

/** Simplified SM-2 intervals in days: 1 → 3 → 7 → 14 */
export const SRS_INTERVALS_DAYS = [1, 3, 7, 14] as const

const MS_PER_DAY = 86_400_000

export function nextIntervalDays(wrongCount: number): number {
  const idx = Math.min(wrongCount - 1, SRS_INTERVALS_DAYS.length - 1)
  return SRS_INTERVALS_DAYS[Math.max(0, idx)]
}

export function computeDue(lastWrongAt: number, intervalDays: number): number {
  return lastWrongAt + intervalDays * MS_PER_DAY
}

export function createSrsRecord(questionId: string, now = Date.now()): SrsRecord {
  const interval = SRS_INTERVALS_DAYS[0]
  return {
    questionId,
    wrongCount: 1,
    lastWrongAt: now,
    due: computeDue(now, interval),
    interval,
    ease: 2.5,
  }
}

export function advanceSrsRecord(record: SrsRecord, now = Date.now()): SrsRecord {
  const wrongCount = record.wrongCount + 1
  const interval = nextIntervalDays(wrongCount)
  return {
    ...record,
    wrongCount,
    lastWrongAt: now,
    due: computeDue(now, interval),
    interval,
  }
}

export async function recordWrongAnswer(questionId: string, now = Date.now()): Promise<void> {
  const normalized = normalizeQuestionId(questionId)
  const existing = await db.srs.get(normalized)
  if (existing) {
    await db.srs.put(advanceSrsRecord(existing, now))
  } else {
    await db.srs.put(createSrsRecord(normalized, now))
  }
}

export async function recordCorrectReview(questionId: string): Promise<void> {
  const normalized = normalizeQuestionId(questionId)
  await db.srs.delete(normalized)
}

export async function getDueQuestionIds(now = Date.now()): Promise<string[]> {
  const due = await db.srs.where('due').belowOrEqual(now).toArray()
  return due.map((r) => r.questionId)
}

export async function getMistakeQuestionIds(): Promise<string[]> {
  const records = await db.srs.orderBy('lastWrongAt').reverse().toArray()
  return records.map((r) => r.questionId)
}

function normalizeQuestionId(id: string): string {
  return id.replace(/__dup\d+$/, '').replace(/__fill\d+$/, '')
}

export function pickDaily10Questions(
  allQuestions: { id: string }[],
  dueIds: string[],
  seenIds: Set<string>,
  count = 10,
): string[] {
  const pool = new Map(allQuestions.map((q) => [q.id, q]))
  const picked: string[] = []
  const used = new Set<string>()

  for (const id of dueIds) {
    if (picked.length >= count) break
    const base = normalizeQuestionId(id)
    if (pool.has(base) && !used.has(base)) {
      picked.push(base)
      used.add(base)
    }
  }

  const fresh = allQuestions.filter((q) => !seenIds.has(q.id) && !used.has(q.id))
  const review = allQuestions.filter((q) => seenIds.has(q.id) && !used.has(q.id))

  const shuffle = <T>(arr: T[]): T[] => {
    const copy = [...arr]
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[copy[i], copy[j]] = [copy[j], copy[i]]
    }
    return copy
  }

  for (const q of shuffle(fresh.length > 0 ? fresh : review)) {
    if (picked.length >= count) break
    if (!used.has(q.id)) {
      picked.push(q.id)
      used.add(q.id)
    }
  }

  return picked.slice(0, count)
}

export async function processAttemptAnswers(
  answers: { questionId: string; correct: boolean }[],
): Promise<void> {
  for (const ans of answers) {
    if (!ans.correct) {
      await recordWrongAnswer(ans.questionId)
    }
  }
}
