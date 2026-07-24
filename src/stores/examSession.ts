import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ExamEngine, type SectionIndices, type SectionKey } from '@/core/engine/stateMachine'
import { ExamTimer, type ExamTimerSerialized } from '@/core/engine/timer'
import { computeScore, computeBand } from '@/core/engine/scoring'
import { EXAM } from '@/core/examConstants'
import { processAttemptAnswers } from '@/core/srs/index'
import { buildDailyFromAnswers } from '@/core/stats'
import { requestPersistentStorage } from '@/core/storage'
import { db } from '@/db/index'
import type { AnswerGiven, ExamConfig, Question, ScoreResult, Band } from '@/core/types'

export type ExamMode = 'real' | 'full-untimed' | 'free' | 'custom'
export type SessionState =
  | 'configuring'
  | 'running'
  | 'breakOffered'
  | 'onBreak'
  | 'reviewingSection'
  | 'paused'
  | 'submitted'
  | 'scored'
  | 'quit'

export interface SessionSnapshot {
  engine: ReturnType<ExamEngine['serialize']>
  timer: ExamTimerSerialized
  timerVisible: boolean
  startedAt: number
}

const AUTOSAVE_MS = 5000

export const useExamSessionStore = defineStore('examSession', () => {
  const state = ref<SessionState>('configuring')
  const mode = ref<ExamMode>('free')
  const isInProgress = ref(false)
  const engine = ref<ExamEngine | null>(null)
  const timer = ref<ExamTimer | null>(null)
  const questions = ref<Question[]>([])
  const currentIndex = ref(0)
  const config = ref<ExamConfig | null>(null)
  const answers = ref(new Map<string, AnswerGiven>())
  const attemptId = ref('')
  const band = ref<Band | null>(null)
  const sectionIndices = ref<SectionIndices>({ a: [], b: [], c: [] })
  const currentSection = ref<SectionKey>('a')
  const lockedSections = ref(new Set<SectionKey>())
  const breakNumber = ref(0)
  const timerVisible = ref(true)
  const startedAt = ref(0)

  let autosaveTimer: ReturnType<typeof setTimeout> | null = null
  let pendingAutosave = false

  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)
  const totalQuestions = computed(() => questions.value.length)
  const isFirst = computed(() => currentIndex.value === 0)
  const isLast = computed(() => currentIndex.value >= questions.value.length - 1)

  const sectionLabel = computed(() => {
    if (mode.value !== 'real') return ''
    const labels: Record<SectionKey, string> = {
      a: 'exam.sectionA',
      b: 'exam.sectionB',
      c: 'exam.sectionC',
    }
    return labels[currentSection.value] ?? ''
  })

  function syncFromEngine(): void {
    if (!engine.value) return
    state.value = engine.value.getState()
    currentIndex.value = engine.value.getCurrentIndex()
    questions.value = engine.value.getQuestions()
    config.value = engine.value.getConfig()
    answers.value = new Map(engine.value.getAnswers())
    attemptId.value = engine.value.getAttemptId()
    mode.value = engine.value.getConfig()?.mode ?? 'free'
    isInProgress.value = engine.value.isInProgress()
    sectionIndices.value = engine.value.getSections()
    currentSection.value = engine.value.getCurrentSection()
    lockedSections.value = new Set(engine.value.getLockedSections())
    breakNumber.value = engine.value.getBreakNumber()
  }

  function scheduleAutosave(): void {
    pendingAutosave = true
    if (autosaveTimer) return
    autosaveTimer = setTimeout(async () => {
      autosaveTimer = null
      if (pendingAutosave) {
        pendingAutosave = false
        await persistSession()
      }
    }, AUTOSAVE_MS)
  }

  async function persistSession(): Promise<void> {
    if (!engine.value || !config.value) return
    if (!engine.value.isInProgress()) return

    const snapshot: SessionSnapshot = {
      engine: engine.value.serialize(),
      timer: timer.value?.serialize() ?? {
        mode: config.value.timerMode,
        totalSeconds: config.value.timerSeconds,
        startedAt: null,
        pausedAt: null,
        pausedAccum: 0,
      },
      timerVisible: timerVisible.value,
      startedAt: startedAt.value,
    }

    const score = computeScore(questions.value, answers.value)

    await db.attempts.put({
      id: attemptId.value,
      mode: config.value.mode,
      startedAt: startedAt.value,
      finishedAt: null,
      durationSec: timer.value?.getElapsed() ?? 0,
      config: { ...config.value, snapshot },
      score: {
        raw: score.raw,
        max: score.max,
        pct: score.pct,
        byDomain: score.byDomain,
        byTask: score.byTask,
        byType: score.byType,
        byApproach: score.byApproach,
      },
      band: null,
      passedProxy: null,
      status: 'in-progress',
    })

    const answerRecords = [...answers.value.entries()].map(([questionId, ans]) => ({
      id: `${attemptId.value}_${questionId}`,
      attemptId: attemptId.value,
      questionId,
      given: ans.given,
      correct: ans.correct,
      timeSec: ans.timeSec,
      flagged: ans.flagged,
      changedCount: ans.changedCount,
      answeredAt: Date.now(),
    }))

    if (answerRecords.length > 0) {
      await db.answers.bulkPut(answerRecords)
    }
  }

  async function writeHistory(status: 'completed' | 'quit'): Promise<void> {
    if (!engine.value || !config.value) return

    const score = computeScore(questions.value, answers.value)
    const pct = score.pct
    const computedBand = computeBand(pct)
    const finishedAt = Date.now()

    await db.attempts.put({
      id: attemptId.value,
      mode: config.value.mode,
      startedAt: startedAt.value,
      finishedAt,
      durationSec: timer.value?.getElapsed() ?? 0,
      config: config.value as unknown as Record<string, unknown>,
      score: {
        raw: score.raw,
        max: score.max,
        pct: score.pct,
        byDomain: score.byDomain,
        byTask: score.byTask,
        byType: score.byType,
        byApproach: score.byApproach,
      },
      band: computedBand,
      passedProxy: pct >= EXAM.PASS_PROXY_PCT,
      status,
    })

    const answerRecords = [...answers.value.entries()].map(([questionId, ans]) => ({
      id: `${attemptId.value}_${questionId}`,
      attemptId: attemptId.value,
      questionId,
      given: ans.given,
      correct: ans.correct,
      timeSec: ans.timeSec,
      flagged: ans.flagged,
      changedCount: ans.changedCount,
      answeredAt: finishedAt,
    }))

    if (answerRecords.length > 0) {
      await db.answers.bulkPut(answerRecords)
    }

    if (status === 'completed') {
      await processAttemptAnswers(answerRecords)
      const allAnswers = await db.answers.toArray()
      const dailyRecords = buildDailyFromAnswers(allAnswers)
      if (dailyRecords.length > 0) {
        await db.daily.bulkPut(dailyRecords)
      }

      const priorCompleted = await db.attempts
        .where('status')
        .equals('completed')
        .count()
      if (priorCompleted <= 1) {
        await requestPersistentStorage()
      }
    }
  }

  async function getRecentQuestionIds(limit = 2): Promise<string[]> {
    const attempts = await db.attempts
      .where('mode')
      .equals('real')
      .reverse()
      .limit(limit)
      .toArray()

    const ids = new Set<string>()
    for (const attempt of attempts) {
      const attemptAnswers = await db.answers.where('attemptId').equals(attempt.id).toArray()
      for (const ans of attemptAnswers) {
        ids.add(ans.questionId.replace(/__dup\d+$/, '').replace(/__fill\d+$/, ''))
      }
    }
    return [...ids]
  }

  async function findInProgressAttempt(): Promise<SessionSnapshot | null> {
    const attempt = await db.attempts.where('status').equals('in-progress').first()
    if (!attempt) return null
    const snapshot = (attempt.config as unknown as ExamConfig & { snapshot?: SessionSnapshot })
      .snapshot
    return snapshot ?? null
  }

  async function discardInProgress(): Promise<void> {
    const attempt = await db.attempts.where('status').equals('in-progress').first()
    if (attempt) {
      await db.answers.where('attemptId').equals(attempt.id).delete()
      await db.attempts.delete(attempt.id)
    }
  }

  function startSession(
    examConfig: ExamConfig,
    examQuestions: Question[],
    sections?: SectionIndices,
    existingAttemptId?: string,
  ): void {
    reset()

    const instance = new ExamEngine()
    instance.start(examConfig, examQuestions, sections, existingAttemptId)
    engine.value = instance
    startedAt.value = Date.now()

    timer.value = new ExamTimer(examConfig.timerMode, examConfig.timerSeconds)
    if (examConfig.timerMode !== 'off') {
      timer.value.start()
      timer.value.onExpire(() => submit())
    }

    syncFromEngine()
    scheduleAutosave()
  }

  async function resumeSession(snapshot: SessionSnapshot): Promise<void> {
    reset()

    engine.value = ExamEngine.deserialize(snapshot.engine)
    timer.value = ExamTimer.deserialize(snapshot.timer)
    timerVisible.value = snapshot.timerVisible
    startedAt.value = snapshot.startedAt

    syncFromEngine()
  }

  function answer(questionId: string, given: unknown): void {
    engine.value?.answer(questionId, given)
    syncFromEngine()
    scheduleAutosave()
  }

  function toggleFlag(questionId: string): void {
    engine.value?.toggleFlag(questionId)
    syncFromEngine()
    scheduleAutosave()
  }

  function next(): boolean {
    const moved = engine.value?.next() ?? false
    syncFromEngine()
    scheduleAutosave()
    return moved
  }

  function previous(): void {
    engine.value?.previous()
    syncFromEngine()
  }

  function goTo(index: number): void {
    engine.value?.goTo(index)
    syncFromEngine()
  }

  function enterSectionReview(): void {
    engine.value?.enterSectionReview()
    syncFromEngine()
  }

  function startBreak(): void {
    engine.value?.startBreak()
    syncFromEngine()
    scheduleAutosave()
  }

  function skipBreak(): void {
    engine.value?.skipBreak()
    syncFromEngine()
    scheduleAutosave()
  }

  function resumeFromBreak(): void {
    engine.value?.resumeFromBreak()
    syncFromEngine()
    scheduleAutosave()
  }

  function isIndexLocked(index: number): boolean {
    return engine.value?.isIndexLocked(index) ?? false
  }

  function getSectionQuestions(section: SectionKey): { index: number; answered: boolean; flagged: boolean }[] {
    const indices = sectionIndices.value[section]
    return indices.map((index) => {
      const q = questions.value[index]
      const ans = q ? answers.value.get(q.id) : undefined
      return {
        index,
        answered: ans?.given != null,
        flagged: ans?.flagged ?? false,
      }
    })
  }

  async function submit(): Promise<void> {
    engine.value?.submit()
    timer.value?.destroy()
    timer.value = null

    if (autosaveTimer) {
      clearTimeout(autosaveTimer)
      autosaveTimer = null
    }
    pendingAutosave = false

    syncFromEngine()

    const score = getScore()
    if (score) band.value = computeBand(score.pct)
    await writeHistory('completed')
  }

  async function quit(): Promise<void> {
    engine.value?.quit()
    timer.value?.destroy()
    timer.value = null

    if (autosaveTimer) {
      clearTimeout(autosaveTimer)
      autosaveTimer = null
    }
    pendingAutosave = false

    syncFromEngine()

    const score = getScore()
    if (score) band.value = computeBand(score.pct)
    await writeHistory('quit')
  }

  function getScore(): ScoreResult | null {
    if (questions.value.length === 0) return null
    return computeScore(questions.value, answers.value)
  }

  function toggleTimerVisible(): void {
    timerVisible.value = !timerVisible.value
    scheduleAutosave()
  }

  function reset(): void {
    if (autosaveTimer) {
      clearTimeout(autosaveTimer)
      autosaveTimer = null
    }
    pendingAutosave = false

    timer.value?.destroy()
    timer.value = null
    engine.value?.reset()
    engine.value = null

    state.value = 'configuring'
    mode.value = 'free'
    isInProgress.value = false
    questions.value = []
    currentIndex.value = 0
    config.value = null
    answers.value = new Map()
    attemptId.value = ''
    band.value = null
    sectionIndices.value = { a: [], b: [], c: [] }
    currentSection.value = 'a'
    lockedSections.value = new Set()
    breakNumber.value = 0
    timerVisible.value = true
    startedAt.value = 0
  }

  function isFlagged(questionId: string): boolean {
    return answers.value.get(questionId)?.flagged ?? false
  }

  function getAnswer(questionId: string): AnswerGiven | undefined {
    return answers.value.get(questionId)
  }

  function getTimeRemaining(): number {
    return timer.value?.getRemaining() ?? 0
  }

  function getTimeElapsed(): number {
    return timer.value?.getElapsed() ?? 0
  }

  return {
    state,
    mode,
    isInProgress,
    engine,
    timer,
    questions,
    currentIndex,
    config,
    answers,
    attemptId,
    band,
    sectionIndices,
    currentSection,
    lockedSections,
    breakNumber,
    timerVisible,
    startedAt,
    currentQuestion,
    totalQuestions,
    isFirst,
    isLast,
    sectionLabel,
    startSession,
    resumeSession,
    answer,
    toggleFlag,
    next,
    previous,
    goTo,
    enterSectionReview,
    startBreak,
    skipBreak,
    resumeFromBreak,
    isIndexLocked,
    getSectionQuestions,
    submit,
    quit,
    getScore,
    reset,
    isFlagged,
    getAnswer,
    getTimeRemaining,
    getTimeElapsed,
    toggleTimerVisible,
    scheduleAutosave,
    persistSession,
    findInProgressAttempt,
    discardInProgress,
    getRecentQuestionIds,
  }
})
