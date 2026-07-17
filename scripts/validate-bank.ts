import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const QUESTIONS_DIR = join(process.cwd(), 'public', 'questions')

interface LText {
  en: string
  zh: string
}
interface QuestionRaw {
  id: string
  type: string
  domain: string
  task: string
  approach: string
  difficulty: number
  stem: LText
  explanation: LText
  options?: LText[]
  correct?: number | number[] | string[]
  selectN?: number
  left?: LText[]
  right?: LText[]
  media?: string
  regions?: { id: string; label: LText }[]
  blanks?: { id: string; options: LText[]; correct: number }[]
  caseId?: string
  refs?: string[]
  tags?: string[]
}

const VALID_TYPES = ['mcq', 'multi', 'matching', 'enhanced-matching', 'hotspot', 'pulldown', 'graphic-mcq']
const VALID_DOMAINS = ['people', 'process', 'business']
const VALID_APPROACHES = ['predictive', 'agile', 'hybrid']

let errors = 0
let warnings = 0

function err(msg: string) {
  console.error(`  ERROR: ${msg}`)
  errors++
}

function warn(msg: string) {
  console.warn(`  WARN: ${msg}`)
  warnings++
}

function validateLText(t: unknown, field: string, qid: string): boolean {
  if (!t || typeof t !== 'object') {
    err(`${qid}: ${field} is not an LText object`)
    return false
  }
  const lt = t as LText
  if (!lt.en || lt.en.trim().length === 0) {
    err(`${qid}: ${field}.en is empty`)
    return false
  }
  if (!lt.zh || lt.zh.trim().length === 0) {
    err(`${qid}: ${field}.zh is empty`)
    return false
  }
  return true
}

function validateQuestion(q: QuestionRaw): void {
  if (!q.id) { err('Missing question id'); return }
  if (!VALID_TYPES.includes(q.type)) err(`${q.id}: invalid type "${q.type}"`)
  if (!VALID_DOMAINS.includes(q.domain)) err(`${q.id}: invalid domain "${q.domain}"`)
  if (!VALID_APPROACHES.includes(q.approach)) err(`${q.id}: invalid approach "${q.approach}"`)
  if (![1, 2, 3].includes(q.difficulty)) err(`${q.id}: invalid difficulty ${q.difficulty}`)
  if (!q.task) err(`${q.id}: missing task`)

  validateLText(q.stem, 'stem', q.id)
  validateLText(q.explanation, 'explanation', q.id)

  if (q.explanation) {
    const expLen = (q.explanation as LText).en?.split(/\s+/).length ?? 0
    if (expLen < 20) warn(`${q.id}: explanation.en is very short (${expLen} words)`)
  }

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq': {
      if (!Array.isArray(q.options) || q.options.length < 2)
        err(`${q.id}: mcq needs >=2 options`)
      if (typeof q.correct !== 'number')
        err(`${q.id}: mcq correct must be a number`)
      else if (q.options && (q.correct < 0 || q.correct >= q.options.length))
        err(`${q.id}: correct index ${q.correct} out of bounds`)
      q.options?.forEach((o, i) => validateLText(o, `options[${i}]`, q.id))
      break
    }
    case 'multi': {
      if (!Array.isArray(q.options) || q.options.length < 3)
        err(`${q.id}: multi needs >=3 options`)
      if (!Array.isArray(q.correct))
        err(`${q.id}: multi correct must be an array`)
      if (typeof q.selectN !== 'number' || q.selectN < 2)
        err(`${q.id}: multi selectN must be >= 2`)
      if (Array.isArray(q.correct) && q.selectN && q.correct.length !== q.selectN)
        err(`${q.id}: correct.length (${q.correct.length}) !== selectN (${q.selectN})`)
      q.options?.forEach((o, i) => validateLText(o, `options[${i}]`, q.id))
      break
    }
    case 'matching':
    case 'enhanced-matching': {
      if (!Array.isArray(q.left) || q.left.length < 2)
        err(`${q.id}: matching needs >=2 left items`)
      if (!Array.isArray(q.right) || q.right.length < 2)
        err(`${q.id}: matching needs >=2 right items`)
      if (!Array.isArray(q.correct))
        err(`${q.id}: matching correct must be an array`)
      if (q.left && q.correct && q.left.length !== (q.correct as number[]).length)
        err(`${q.id}: left.length !== correct.length`)
      q.left?.forEach((o, i) => validateLText(o, `left[${i}]`, q.id))
      q.right?.forEach((o, i) => validateLText(o, `right[${i}]`, q.id))
      break
    }
    case 'hotspot': {
      if (!q.media) err(`${q.id}: hotspot needs media`)
      if (!Array.isArray(q.regions) || q.regions.length < 2)
        err(`${q.id}: hotspot needs >=2 regions`)
      if (!Array.isArray(q.correct) || q.correct.length < 1)
        err(`${q.id}: hotspot needs >=1 correct region`)
      break
    }
    case 'pulldown': {
      if (!Array.isArray(q.blanks) || q.blanks.length < 1)
        err(`${q.id}: pulldown needs >=1 blank`)
      q.blanks?.forEach((b, i) => {
        if (!Array.isArray(b.options) || b.options.length < 2)
          err(`${q.id}: blank[${i}] needs >=2 options`)
        if (typeof b.correct !== 'number')
          err(`${q.id}: blank[${i}].correct must be a number`)
        b.options?.forEach((o, j) => validateLText(o, `blank[${i}].options[${j}]`, q.id))
      })
      break
    }
  }

  if (q.type === 'graphic-mcq' && !q.media)
    warn(`${q.id}: graphic-mcq without media`)
  if (q.media) {
    const mediaPath = join(QUESTIONS_DIR, 'media', q.media)
    if (!existsSync(mediaPath)) warn(`${q.id}: media file not found: ${q.media}`)
  }
}

function main() {
  console.log('Validating question bank...\n')

  const manifestPath = join(QUESTIONS_DIR, 'manifest.json')
  if (!existsSync(manifestPath)) {
    console.error('manifest.json not found')
    process.exit(1)
  }

  const manifest = JSON.parse(readFileSync(manifestPath, 'utf-8'))
  console.log(`Bank version: ${manifest.version}`)
  console.log(`Declared total: ${manifest.counts.total}\n`)

  const allQuestions: QuestionRaw[] = []
  const ids = new Set<string>()

  for (const chunk of manifest.chunks) {
    const chunkPath = join(QUESTIONS_DIR, chunk.file)
    if (!existsSync(chunkPath)) {
      err(`Chunk file not found: ${chunk.file}`)
      continue
    }
    const questions = JSON.parse(readFileSync(chunkPath, 'utf-8')) as QuestionRaw[]
    if (questions.length !== chunk.count) {
      warn(`${chunk.file}: declared ${chunk.count} questions, found ${questions.length}`)
    }
    for (const q of questions) {
      if (ids.has(q.id)) err(`Duplicate id: ${q.id}`)
      ids.add(q.id)
      validateQuestion(q)
      allQuestions.push(q)
    }
  }

  for (const caseFile of manifest.cases) {
    const casePath = join(QUESTIONS_DIR, caseFile.file)
    if (!existsSync(casePath)) {
      err(`Case file not found: ${caseFile.file}`)
      continue
    }
    const cases = JSON.parse(readFileSync(casePath, 'utf-8'))
    for (const c of cases) {
      if (!c.id) err('Case missing id')
      if (!c.scenario) err(`${c.id}: case missing scenario`)
      else validateLText(c.scenario, 'scenario', c.id)
      if (!Array.isArray(c.questionIds) || c.questionIds.length < 2)
        warn(`${c.id}: case has <2 questions`)
    }
  }

  const domainCounts: Record<string, number> = {}
  const typeCounts: Record<string, number> = {}
  const approachCounts: Record<string, number> = {}
  const difficultyCounts: Record<number, number> = {}
  const taskCounts: Record<string, number> = {}

  for (const q of allQuestions) {
    domainCounts[q.domain] = (domainCounts[q.domain] ?? 0) + 1
    typeCounts[q.type] = (typeCounts[q.type] ?? 0) + 1
    approachCounts[q.approach] = (approachCounts[q.approach] ?? 0) + 1
    difficultyCounts[q.difficulty] = (difficultyCounts[q.difficulty] ?? 0) + 1
    taskCounts[q.task] = (taskCounts[q.task] ?? 0) + 1
  }

  console.log('--- Distribution Report ---')
  console.log(`Total questions: ${allQuestions.length}`)
  console.log('\nBy domain:', domainCounts)
  console.log('By type:', typeCounts)
  console.log('By approach:', approachCounts)
  console.log('By difficulty:', difficultyCounts)
  console.log('By task:', taskCounts)

  console.log(`\n--- Summary ---`)
  console.log(`Errors: ${errors}`)
  console.log(`Warnings: ${warnings}`)

  if (errors > 0) {
    console.error('\nValidation FAILED')
    process.exit(1)
  }
  console.log('\nValidation PASSED')
}

main()
