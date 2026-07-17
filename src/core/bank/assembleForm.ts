import { EXAM, ECO_TASKS } from '../examConstants'
import type { Approach, CaseSet, Difficulty, Domain, Question, QType } from '../types'

export interface AssembleFormOptions {
  questions: Question[]
  cases: CaseSet[]
  seed: number
  exclude?: string[]
  onvue?: boolean
}

export interface AssembleFormResult {
  questions: Question[]
  sections: { a: number[]; b: number[]; c: number[] }
  seed: number
}

const ONVUE_EXCLUDED_TYPES: QType[] = [
  'matching',
  'enhanced-matching',
  'hotspot',
  'pulldown',
]

const ALL_TASKS: string[] = [
  ...ECO_TASKS.people.map((t) => t.id),
  ...ECO_TASKS.process.map((t) => t.id),
  ...ECO_TASKS.business.map((t) => t.id),
]

function mulberry32(seed: number): () => number {
  let s = seed >>> 0
  return () => {
    s = (s + 0x6d2b79f5) | 0
    let t = Math.imul(s ^ (s >>> 15), 1 | s)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function shuffleWithRng<T>(arr: T[], rng: () => number): T[] {
  const result = [...arr]
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

function domainTargets(total: number): Record<Domain, number> {
  const people = Math.round(total * EXAM.DOMAIN_WEIGHTS.people)
  const process = Math.round(total * EXAM.DOMAIN_WEIGHTS.process)
  const business = total - people - process
  return { people, process, business }
}

function approachTargets(total: number): Record<Approach, number> {
  return {
    predictive: Math.round(total * EXAM.APPROACH_MIX.predictive),
    agile: Math.round(total * EXAM.APPROACH_MIX.agile),
    hybrid: total - Math.round(total * EXAM.APPROACH_MIX.predictive) - Math.round(total * EXAM.APPROACH_MIX.agile),
  }
}

function difficultyTargets(total: number): Record<Difficulty, number> {
  const easy = Math.round(total * EXAM.DIFFICULTY_MIX[1])
  const medium = Math.round(total * EXAM.DIFFICULTY_MIX[2])
  const hard = total - easy - medium
  return { 1: easy, 2: medium, 3: hard }
}

function isOnvueCompatible(q: Question, onvue: boolean): boolean {
  if (!onvue) return true
  return !ONVUE_EXCLUDED_TYPES.includes(q.type)
}

function pickBest(
  pool: Question[],
  needed: Question[],
  targets: {
    domain: Record<Domain, number>
    approach: Record<Approach, number>
    difficulty: Record<Difficulty, number>
    tasks: Set<string>
  },
  rng: () => number,
): Question | null {
  if (pool.length === 0) return null

  const counts = {
    domain: { people: 0, process: 0, business: 0 } as Record<Domain, number>,
    approach: { predictive: 0, agile: 0, hybrid: 0 } as Record<Approach, number>,
    difficulty: { 1: 0, 2: 0, 3: 0 } as Record<Difficulty, number>,
  }

  for (const q of needed) {
    counts.domain[q.domain] += 1
    counts.approach[q.approach] += 1
    counts.difficulty[q.difficulty] += 1
  }

  const scored = pool.map((q) => {
    let score = rng() * 0.01
    if (counts.domain[q.domain] < targets.domain[q.domain]) score += 3
    if (counts.approach[q.approach] < targets.approach[q.approach]) score += 2
    if (counts.difficulty[q.difficulty] < targets.difficulty[q.difficulty]) score += 2
    if (targets.tasks.has(q.task)) score += 5
    return { q, score }
  })

  scored.sort((a, b) => b.score - a.score)
  return scored[0]?.q ?? null
}

function selectQuestions(
  pool: Question[],
  count: number,
  rng: () => number,
  domainTgt: Record<Domain, number>,
  requiredTasks: Set<string>,
): Question[] {
  if (count === 0) return []

  const scale = count / EXAM.TOTAL_QUESTIONS
  const scaledDomain: Record<Domain, number> = {
    people: Math.round(domainTgt.people * scale),
    process: Math.round(domainTgt.process * scale),
    business: Math.round(domainTgt.business * scale),
  }
  const diff = count - scaledDomain.people - scaledDomain.process - scaledDomain.business
  scaledDomain.business += diff

  const approachTgt = approachTargets(count)
  const difficultyTgt = difficultyTargets(count)
  const selected: Question[] = []
  const usedIds = new Set<string>()
  let available = shuffleWithRng([...pool], rng)

  for (const taskId of ALL_TASKS) {
    if (!requiredTasks.has(taskId)) continue
    const candidate = available.find((q) => q.task === taskId && !usedIds.has(q.id))
    if (!candidate) continue
    selected.push(candidate)
    usedIds.add(candidate.id)
    available = available.filter((q) => q.id !== candidate.id)
    requiredTasks.delete(taskId)
  }

  while (selected.length < count) {
    available = available.filter((q) => !usedIds.has(q.id))
    if (available.length === 0) {
      if (pool.length === 0) break
      available = shuffleWithRng([...pool], rng)
    }

    const pick = pickBest(
      available,
      selected,
      {
        domain: scaledDomain,
        approach: approachTgt,
        difficulty: difficultyTgt,
        tasks: requiredTasks,
      },
      rng,
    )
    if (!pick) break
    selected.push(pick)
    usedIds.add(pick.id)
    requiredTasks.delete(pick.task)
    available = available.filter((q) => q.id !== pick.id)
  }

  while (selected.length < count && pool.length > 0) {
    const remaining = pool.filter((q) => !usedIds.has(q.id))
    const source = remaining.length > 0 ? remaining : pool
    const pick = source[Math.floor(rng() * source.length)]
    selected.push({ ...pick, id: `${pick.id}__dup${selected.length}` })
    usedIds.add(pick.id)
  }

  return selected.slice(0, count)
}

export function assembleForm(options: AssembleFormOptions): AssembleFormResult {
  const { cases, seed, exclude = [], onvue = false } = options
  const rng = mulberry32(seed)
  const excludeSet = new Set(exclude)

  const questionMap = new Map<string, Question>()
  for (const q of options.questions) {
    questionMap.set(q.id, q)
  }

  let pool = options.questions.filter(
    (q) => !excludeSet.has(q.id) && isOnvueCompatible(q, onvue),
  )

  if (pool.length === 0) {
    pool = options.questions.filter((q) => isOnvueCompatible(q, onvue))
  }

  const fullDomainTgt = domainTargets(EXAM.TOTAL_QUESTIONS)
  const remainingTasks = new Set(ALL_TASKS)

  const eligibleCases = shuffleWithRng(
    cases.filter((c) => c.questionIds.some((id) => questionMap.has(id))),
    rng,
  )

  const sectionAQuestions: Question[] = []
  const usedCaseQuestionIds = new Set<string>()
  let casesUsed = 0

  for (const caseSet of eligibleCases) {
    if (casesUsed >= EXAM.SECTION_A_CASES) break
    const caseQs = caseSet.questionIds
      .map((id) => questionMap.get(id))
      .filter((q): q is Question => q != null && isOnvueCompatible(q, onvue) && !excludeSet.has(q.id))

    if (caseQs.length === 0) continue

    for (const q of caseQs) {
      sectionAQuestions.push(q)
      usedCaseQuestionIds.add(q.id)
      remainingTasks.delete(q.task)
    }
    casesUsed += 1
  }

  while (sectionAQuestions.length < EXAM.SECTION_A_TOTAL && pool.length > 0) {
    const casePool = pool.filter((q) => q.caseId && !usedCaseQuestionIds.has(q.id))
    const source = casePool.length > 0 ? casePool : pool
    const pick = source[Math.floor(rng() * source.length)]
    sectionAQuestions.push(pick)
    usedCaseQuestionIds.add(pick.id)
    remainingTasks.delete(pick.task)
  }

  sectionAQuestions.splice(EXAM.SECTION_A_TOTAL)

  const independentPool = pool.filter((q) => !q.caseId && !usedCaseQuestionIds.has(q.id))
  const sectionBCCount = EXAM.SECTION_B_TOTAL + EXAM.SECTION_C_TOTAL

  const sectionBCQuestions = selectQuestions(
    independentPool.length > 0 ? independentPool : pool.filter((q) => !usedCaseQuestionIds.has(q.id)),
    sectionBCCount,
    rng,
    fullDomainTgt,
    remainingTasks,
  )

  const allQuestions = [...sectionAQuestions, ...sectionBCQuestions]

  while (allQuestions.length < EXAM.TOTAL_QUESTIONS && pool.length > 0) {
    const pick = pool[Math.floor(rng() * pool.length)]
    allQuestions.push({ ...pick, id: `${pick.id}__fill${allQuestions.length}` })
  }

  const finalQuestions = allQuestions.slice(0, EXAM.TOTAL_QUESTIONS)

  const sectionAIndices = Array.from({ length: Math.min(EXAM.SECTION_A_TOTAL, finalQuestions.length) }, (_, i) => i)
  const sectionBStart = sectionAIndices.length
  const sectionBEnd = Math.min(sectionBStart + EXAM.SECTION_B_TOTAL, finalQuestions.length)
  const sectionBIndices = Array.from({ length: sectionBEnd - sectionBStart }, (_, i) => sectionBStart + i)
  const sectionCStart = sectionBEnd
  const sectionCIndices = Array.from(
    { length: finalQuestions.length - sectionCStart },
    (_, i) => sectionCStart + i,
  )

  return {
    questions: finalQuestions,
    sections: {
      a: sectionAIndices,
      b: sectionBIndices,
      c: sectionCIndices,
    },
    seed,
  }
}
