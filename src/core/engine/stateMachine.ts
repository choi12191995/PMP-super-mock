import type { AnswerGiven, ExamConfig, Question } from '../types'
import { isAnswerCorrect } from './scoring'

export type ExamMode = ExamConfig['mode']

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

export class ExamEngine {
  private _state: SessionState = 'configuring'
  private _config: ExamConfig | null = null
  private _questions: Question[] = []
  private _currentIndex = 0
  private _answers = new Map<string, AnswerGiven>()
  private _questionStartAt = Date.now()
  private _attemptId = ''

  getState(): SessionState {
    return this._state
  }

  getConfig(): ExamConfig | null {
    return this._config
  }

  getQuestions(): Question[] {
    return this._questions
  }

  getCurrentIndex(): number {
    return this._currentIndex
  }

  getAnswers(): Map<string, AnswerGiven> {
    return this._answers
  }

  getCurrentQuestion(): Question | null {
    return this._questions[this._currentIndex] ?? null
  }

  getAttemptId(): string {
    return this._attemptId
  }

  isInProgress(): boolean {
    return ['running', 'breakOffered', 'onBreak', 'reviewingSection', 'paused'].includes(
      this._state,
    )
  }

  start(config: ExamConfig, questions: Question[]): void {
    this._config = config
    this._questions =
      config.questionCount >= questions.length
        ? [...questions]
        : questions.slice(0, config.questionCount)
    this._currentIndex = 0
    this._answers.clear()
    this._state = 'running'
    this._attemptId = crypto.randomUUID()
    this._questionStartAt = Date.now()
  }

  answer(questionId: string, given: unknown): void {
    const question = this._questions.find((q) => q.id === questionId)
    if (!question || this._state !== 'running') return

    const existing = this._answers.get(questionId)
    const timeSec = (Date.now() - this._questionStartAt) / 1000
    const correct = isAnswerCorrect(question, given)

    this._answers.set(questionId, {
      questionId,
      given,
      correct,
      timeSec: existing ? existing.timeSec + timeSec : timeSec,
      flagged: existing?.flagged ?? false,
      changedCount: existing ? existing.changedCount + 1 : 0,
    })
  }

  toggleFlag(questionId: string): void {
    const existing = this._answers.get(questionId)
    if (existing) {
      existing.flagged = !existing.flagged
      return
    }

    this._answers.set(questionId, {
      questionId,
      given: null,
      correct: false,
      timeSec: 0,
      flagged: true,
      changedCount: 0,
    })
  }

  next(): void {
    if (this._currentIndex < this._questions.length - 1) {
      this._currentIndex += 1
      this._questionStartAt = Date.now()
    }
  }

  previous(): void {
    if (this._currentIndex > 0) {
      this._currentIndex -= 1
      this._questionStartAt = Date.now()
    }
  }

  goTo(index: number): void {
    if (index >= 0 && index < this._questions.length) {
      this._currentIndex = index
      this._questionStartAt = Date.now()
    }
  }

  submit(): void {
    if (this._state !== 'running') return
    this._state = 'submitted'
    this._state = 'scored'
  }

  quit(): void {
    if (this._state === 'configuring') return
    this._state = 'quit'
  }

  reset(): void {
    this._state = 'configuring'
    this._config = null
    this._questions = []
    this._currentIndex = 0
    this._answers.clear()
    this._attemptId = ''
  }
}
