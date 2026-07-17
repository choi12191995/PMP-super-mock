import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ExamEngine } from '@/core/engine/stateMachine'
import { ExamTimer } from '@/core/engine/timer'
import { computeScore, computeBand } from '@/core/engine/scoring'
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

  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)
  const totalQuestions = computed(() => questions.value.length)
  const isFirst = computed(() => currentIndex.value === 0)
  const isLast = computed(() => currentIndex.value >= questions.value.length - 1)

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
  }

  function startSession(examConfig: ExamConfig, examQuestions: Question[]): void {
    reset()

    const instance = new ExamEngine()
    instance.start(examConfig, examQuestions)
    engine.value = instance

    timer.value = new ExamTimer(examConfig.timerMode, examConfig.timerSeconds)
    if (examConfig.timerMode !== 'off') {
      timer.value.start()
      timer.value.onExpire(() => submit())
    }

    syncFromEngine()
  }

  function answer(questionId: string, given: unknown): void {
    engine.value?.answer(questionId, given)
    syncFromEngine()
  }

  function toggleFlag(questionId: string): void {
    engine.value?.toggleFlag(questionId)
    syncFromEngine()
  }

  function next(): void {
    engine.value?.next()
    syncFromEngine()
  }

  function previous(): void {
    engine.value?.previous()
    syncFromEngine()
  }

  function goTo(index: number): void {
    engine.value?.goTo(index)
    syncFromEngine()
  }

  function submit(): void {
    engine.value?.submit()
    timer.value?.destroy()
    timer.value = null
    syncFromEngine()

    const score = getScore()
    if (score) band.value = computeBand(score.pct)
  }

  function quit(): void {
    engine.value?.quit()
    timer.value?.destroy()
    timer.value = null
    syncFromEngine()

    const score = getScore()
    if (score) band.value = computeBand(score.pct)
  }

  function getScore(): ScoreResult | null {
    if (questions.value.length === 0) return null
    return computeScore(questions.value, answers.value)
  }

  function reset(): void {
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
  }

  function isFlagged(questionId: string): boolean {
    return answers.value.get(questionId)?.flagged ?? false
  }

  function getAnswer(questionId: string): AnswerGiven | undefined {
    return answers.value.get(questionId)
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
    currentQuestion,
    totalQuestions,
    isFirst,
    isLast,
    startSession,
    answer,
    toggleFlag,
    next,
    previous,
    goTo,
    submit,
    quit,
    getScore,
    reset,
    isFlagged,
    getAnswer,
  }
})
