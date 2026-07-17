import type { AnswerGiven, ExamConfig, Question } from '../types'
import { isAnswerCorrect } from './scoring'

export type ExamMode = ExamConfig['mode']
export type SectionKey = 'a' | 'b' | 'c'

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

export interface SectionIndices {
  a: number[]
  b: number[]
  c: number[]
}

export interface ExamEngineSerialized {
  state: SessionState
  config: ExamConfig
  questions: Question[]
  currentIndex: number
  answers: [string, AnswerGiven][]
  attemptId: string
  sections: SectionIndices
  lockedSections: SectionKey[]
  currentSection: SectionKey
  breakNumber: number
  questionStartAt: number
}

export class ExamEngine {
  private _state: SessionState = 'configuring'
  private _config: ExamConfig | null = null
  private _questions: Question[] = []
  private _currentIndex = 0
  private _answers = new Map<string, AnswerGiven>()
  private _questionStartAt = Date.now()
  private _attemptId = ''
  private _sections: SectionIndices = { a: [], b: [], c: [] }
  private _lockedSections = new Set<SectionKey>()
  private _currentSection: SectionKey = 'a'
  private _breakNumber = 0

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

  getSections(): SectionIndices {
    return this._sections
  }

  getLockedSections(): Set<SectionKey> {
    return this._lockedSections
  }

  getCurrentSection(): SectionKey {
    return this._currentSection
  }

  getBreakNumber(): number {
    return this._breakNumber
  }

  isInProgress(): boolean {
    return ['running', 'breakOffered', 'onBreak', 'reviewingSection', 'paused'].includes(
      this._state,
    )
  }

  hasSectionLocks(): boolean {
    return this._config?.mode === 'real'
  }

  getSectionForIndex(index: number): SectionKey | null {
    if (this._sections.a.includes(index)) return 'a'
    if (this._sections.b.includes(index)) return 'b'
    if (this._sections.c.includes(index)) return 'c'
    return null
  }

  isIndexLocked(index: number): boolean {
    if (!this.hasSectionLocks()) return false
    const section = this.getSectionForIndex(index)
    return section !== null && this._lockedSections.has(section)
  }

  isEndOfSection(): boolean {
    const indices = this._sections[this._currentSection]
    if (indices.length === 0) return false
    return this._currentIndex === indices[indices.length - 1]
  }

  isLastSection(): boolean {
    return this._currentSection === 'c'
  }

  start(
    config: ExamConfig,
    questions: Question[],
    sections?: SectionIndices,
    attemptId?: string,
  ): void {
    this._config = config
    this._questions =
      config.questionCount >= questions.length
        ? [...questions]
        : questions.slice(0, config.questionCount)
    this._currentIndex = 0
    this._answers.clear()
    this._state = 'running'
    this._attemptId = attemptId ?? crypto.randomUUID()
    this._questionStartAt = Date.now()
    this._breakNumber = 0
    this._lockedSections.clear()
    this._currentSection = 'a'

    if (sections) {
      this._sections = {
        a: [...sections.a],
        b: [...sections.b],
        c: [...sections.c],
      }
    } else if (config.mode === 'real') {
      const aEnd = Math.min(20, this._questions.length)
      const bEnd = Math.min(aEnd + 80, this._questions.length)
      this._sections = {
        a: Array.from({ length: aEnd }, (_, i) => i),
        b: Array.from({ length: bEnd - aEnd }, (_, i) => aEnd + i),
        c: Array.from({ length: this._questions.length - bEnd }, (_, i) => bEnd + i),
      }
    } else {
      this._sections = {
        a: [],
        b: Array.from({ length: this._questions.length }, (_, i) => i),
        c: [],
      }
      this._currentSection = 'b'
    }
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
    if (this._state !== 'running') return

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

  next(): boolean {
    if (this._state !== 'running') return false

    if (this.hasSectionLocks() && this.isEndOfSection() && !this.isLastSection()) {
      this._state = 'reviewingSection'
      return false
    }

    if (this._currentIndex < this._questions.length - 1) {
      this._currentIndex += 1
      this._questionStartAt = Date.now()
      this.updateCurrentSection()
      return true
    }
    return false
  }

  previous(): void {
    if (this._state !== 'running') return

    const target = this._currentIndex - 1
    if (target >= 0 && !this.isIndexLocked(target)) {
      this._currentIndex = target
      this._questionStartAt = Date.now()
      this.updateCurrentSection()
    }
  }

  goTo(index: number): void {
    if (this._state !== 'running' && this._state !== 'reviewingSection') return
    if (index >= 0 && index < this._questions.length && !this.isIndexLocked(index)) {
      this._currentIndex = index
      this._questionStartAt = Date.now()
      this.updateCurrentSection()
      if (this._state === 'reviewingSection') {
        this._state = 'running'
      }
    }
  }

  enterSectionReview(): void {
    if (this._state === 'running' && this.hasSectionLocks()) {
      this._state = 'reviewingSection'
    }
  }

  startBreak(): void {
    if (this._state !== 'reviewingSection') return
    this._lockedSections.add(this._currentSection)
    this._breakNumber += 1
    this._state = 'onBreak'
  }

  skipBreak(): void {
    if (this._state !== 'onBreak') return
    this.resumeFromBreak()
  }

  resumeFromBreak(): void {
    if (this._state !== 'onBreak') return

    if (this._currentSection === 'a') {
      this._currentSection = 'b'
      this._currentIndex = this._sections.b[0] ?? this._currentIndex
    } else if (this._currentSection === 'b') {
      this._currentSection = 'c'
      this._currentIndex = this._sections.c[0] ?? this._currentIndex
    }

    this._questionStartAt = Date.now()
    this._state = 'running'
  }

  submit(): void {
    if (this._state !== 'running' && this._state !== 'reviewingSection') return
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
    this._sections = { a: [], b: [], c: [] }
    this._lockedSections.clear()
    this._currentSection = 'a'
    this._breakNumber = 0
  }

  serialize(): ExamEngineSerialized {
    return {
      state: this._state,
      config: this._config!,
      questions: this._questions,
      currentIndex: this._currentIndex,
      answers: [...this._answers.entries()],
      attemptId: this._attemptId,
      sections: this._sections,
      lockedSections: [...this._lockedSections],
      currentSection: this._currentSection,
      breakNumber: this._breakNumber,
      questionStartAt: this._questionStartAt,
    }
  }

  static deserialize(data: ExamEngineSerialized): ExamEngine {
    const engine = new ExamEngine()
    engine._state = data.state
    engine._config = data.config
    engine._questions = data.questions
    engine._currentIndex = data.currentIndex
    engine._answers = new Map(data.answers)
    engine._attemptId = data.attemptId
    engine._sections = data.sections
    engine._lockedSections = new Set(data.lockedSections)
    engine._currentSection = data.currentSection
    engine._breakNumber = data.breakNumber
    engine._questionStartAt = data.questionStartAt
    return engine
  }

  private updateCurrentSection(): void {
    const section = this.getSectionForIndex(this._currentIndex)
    if (section) this._currentSection = section
  }
}
