<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import McqRenderer from '@/components/question-types/McqRenderer.vue'
import MultiRenderer from '@/components/question-types/MultiRenderer.vue'
import MatchingRenderer from '@/components/question-types/MatchingRenderer.vue'
import HotspotRenderer from '@/components/question-types/HotspotRenderer.vue'
import PulldownRenderer from '@/components/question-types/PulldownRenderer.vue'
import GraphicMcqRenderer from '@/components/question-types/GraphicMcqRenderer.vue'
import CaseSetRenderer from '@/components/question-types/CaseSetRenderer.vue'
import TimerBar from '@/components/exam/TimerBar.vue'
import BreakScreen from '@/components/exam/BreakScreen.vue'
import SectionReviewScreen from '@/components/exam/SectionReviewScreen.vue'
import Calculator from '@/components/exam/Calculator.vue'
import ScratchPad from '@/components/exam/ScratchPad.vue'
import LanguagePeek from '@/components/exam/LanguagePeek.vue'
import ChatFab from '@/components/ai/ChatFab.vue'
import ChatPanel from '@/components/ai/ChatPanel.vue'
import { loadAllCases } from '@/core/bank/loader'
import { useAiStore } from '@/stores/ai'
import { EXAM } from '@/core/examConstants'
import { useExamSessionStore } from '@/stores/examSession'
import { db } from '@/db/index'
import type {
  McqQ,
  MultiQ,
  MatchingQ,
  HotspotQ,
  PulldownQ,
  CaseSet,
  LText,
} from '@/core/types'

const router = useRouter()
const { t, locale } = useI18n()
const session = useExamSessionStore()
const ai = useAiStore()

const showChatPanel = ref(false)

const strikeThroughs = ref(new Map<string, Set<number>>())
const mcqSelection = ref<number | null>(null)
const multiSelection = ref<number[]>([])
const matchingSelection = ref<number[]>([])
const hotspotSelection = ref<string[]>([])
const pulldownSelection = ref<Record<string, number>>({})
const caseMap = ref(new Map<string, CaseSet>())
const timeRemaining = ref(0)
const timeElapsed = ref(0)
const showResumePrompt = ref(false)
const resumeChecked = ref(false)
const showCalculator = ref(false)
const showScratchPad = ref(false)
const scratchPadNotes = ref(new Map<string, string>())
const bookmarkedIds = ref(new Set<string>())
let timerTickInterval: ReturnType<typeof setInterval> | null = null
let wakeLock: WakeLockSentinel | null = null

const lang = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en') as 'en' | 'zh-TW')

const question = computed(() => session.currentQuestion)

const isRealExam = computed(() => session.mode === 'real')
const isOnBreak = computed(() => session.state === 'onBreak')
const isSectionReview = computed(() => session.state === 'reviewingSection')

const sectionLabelText = computed(() => {
  if (!session.sectionLabel) return ''
  return t(session.sectionLabel)
})

const sectionReviewQuestions = computed(() =>
  session.getSectionQuestions(session.currentSection),
)

const breakNumber = computed((): 1 | 2 => (session.breakNumber === 1 ? 1 : 2))

const currentStrikes = computed(() => {
  const q = question.value
  if (!q) return new Set<number>()
  return strikeThroughs.value.get(q.id) ?? new Set<number>()
})

const currentCase = computed((): CaseSet | null => {
  const q = question.value
  if (!q?.caseId) return null
  return caseMap.value.get(q.caseId) ?? null
})

const caseQuestionIndex = computed(() => {
  const q = question.value
  const cs = currentCase.value
  if (!q || !cs) return 0
  const idx = cs.questionIds.indexOf(q.id)
  return idx >= 0 ? idx : 0
})

const caseQuestionTotal = computed(() => currentCase.value?.questionIds.length ?? 0)

function pulldownCorrectAnswer(q: PulldownQ): Record<string, number> {
  return Object.fromEntries(q.blanks.map((b) => [b.id, b.correct]))
}

function isPulldownComplete(q: PulldownQ, selections: Record<string, number>): boolean {
  return q.blanks.every((b) => selections[b.id] !== undefined)
}

const hasAnswer = computed(() => {
  const q = question.value
  if (!q) return false
  const stored = session.getAnswer(q.id)
  if (stored?.given != null) return true
  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      return mcqSelection.value !== null
    case 'multi':
      return multiSelection.value.length === q.selectN
    case 'matching':
    case 'enhanced-matching':
      return matchingSelection.value.length === q.left.length
    case 'hotspot':
      return hotspotSelection.value.length > 0
    case 'pulldown':
      return isPulldownComplete(q, pulldownSelection.value)
    default:
      return false
  }
})

const showFeedback = computed(() => {
  if (!session.config || session.config.feedbackMode !== 'immediate') return false
  const q = question.value
  if (!q) return false
  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      return mcqSelection.value !== null
    case 'multi':
      return multiSelection.value.length === q.selectN
    case 'matching':
    case 'enhanced-matching':
      return matchingSelection.value.length === q.left.length
    case 'hotspot':
      return hotspotSelection.value.length > 0
    case 'pulldown':
      return isPulldownComplete(q, pulldownSelection.value)
    default:
      return false
  }
})

const showChatFab = computed(() => {
  if (!ai.enabled || !ai.isConfigured) return false
  if (!session.config?.aiChat) return false
  if (isRealExam.value && session.isInProgress) return false
  return !!question.value
})

function getCurrentUserAnswer(): unknown {
  const q = question.value
  if (!q) return undefined
  const stored = session.getAnswer(q.id)
  if (stored?.given != null) return stored.given

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      return mcqSelection.value
    case 'multi':
      return multiSelection.value.length ? multiSelection.value : undefined
    case 'matching':
    case 'enhanced-matching':
      return matchingSelection.value.length ? matchingSelection.value : undefined
    case 'hotspot':
      return hotspotSelection.value.length ? hotspotSelection.value : undefined
    case 'pulldown':
      return isPulldownComplete(q, pulldownSelection.value) ? pulldownSelection.value : undefined
    default:
      return undefined
  }
}

function getCorrectAnswer(): unknown {
  const q = question.value
  if (!q) return undefined
  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      return q.correct
    case 'multi':
      return q.correct
    case 'matching':
    case 'enhanced-matching':
      return q.correct
    case 'hotspot':
      return q.correct
    case 'pulldown':
      return pulldownCorrectAnswer(q)
    default:
      return undefined
  }
}

const questionContext = computed(() => {
  const q = question.value
  if (!q) return null
  const userAnswer = getCurrentUserAnswer()
  const isAnswered = showFeedback.value && userAnswer != null
  return {
    question: q,
    userAnswer,
    correctAnswer: isAnswered ? getCorrectAnswer() : undefined,
    isAnswered,
    language: lang.value,
  }
})

const answerDisabled = computed(() => showFeedback.value)

const rendererComponent = computed((): Component | null => {
  const q = question.value
  if (!q) return null
  switch (q.type) {
    case 'mcq':
      return McqRenderer
    case 'graphic-mcq':
      return GraphicMcqRenderer
    case 'multi':
      return MultiRenderer
    case 'matching':
    case 'enhanced-matching':
      return MatchingRenderer
    case 'hotspot':
      return HotspotRenderer
    case 'pulldown':
      return PulldownRenderer
    default:
      return null
  }
})

const rendererProps = computed(() => {
  const q = question.value
  if (!q) return {}

  const base = {
    showFeedback: showFeedback.value,
    disabled: answerDisabled.value,
    lang: lang.value,
  }

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      return {
        ...base,
        question: q as McqQ,
        modelValue: mcqSelection.value,
        correctAnswer: (q as McqQ).correct,
        strikeThroughs: currentStrikes.value,
      }
    case 'multi':
      return {
        ...base,
        question: q as MultiQ,
        modelValue: multiSelection.value,
        correctAnswer: (q as MultiQ).correct,
        strikeThroughs: currentStrikes.value,
      }
    case 'matching':
    case 'enhanced-matching':
      return {
        ...base,
        question: q as MatchingQ,
        modelValue: matchingSelection.value,
        correctAnswer: (q as MatchingQ).correct,
      }
    case 'hotspot':
      return {
        ...base,
        question: q as HotspotQ,
        modelValue: hotspotSelection.value,
        correctAnswer: (q as HotspotQ).correct,
      }
    case 'pulldown':
      return {
        ...base,
        question: q as PulldownQ,
        modelValue: pulldownSelection.value,
        correctAnswer: pulldownCorrectAnswer(q as PulldownQ),
      }
    default:
      return base
  }
})

function ltext(text: LText): string {
  return lang.value === 'zh-TW' ? text.zh : text.en
}

function getScratchPadNotes(questionId: string): string {
  return scratchPadNotes.value.get(questionId) ?? ''
}

function setScratchPadNotes(questionId: string, notes: string): void {
  scratchPadNotes.value.set(questionId, notes)
}

function loadLocalSelection(): void {
  const q = question.value
  if (!q) return

  const stored = session.getAnswer(q.id)

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      mcqSelection.value = typeof stored?.given === 'number' ? stored.given : null
      break
    case 'multi':
      multiSelection.value = Array.isArray(stored?.given)
        ? [...(stored.given as number[])].sort((a, b) => a - b)
        : []
      break
    case 'matching':
    case 'enhanced-matching':
      matchingSelection.value = Array.isArray(stored?.given) ? [...(stored.given as number[])] : []
      break
    case 'hotspot':
      hotspotSelection.value = Array.isArray(stored?.given) ? [...(stored.given as string[])] : []
      break
    case 'pulldown':
      pulldownSelection.value =
        stored?.given && typeof stored.given === 'object' && !Array.isArray(stored.given)
          ? { ...(stored.given as Record<string, number>) }
          : {}
      break
  }
}

function onRendererUpdate(value: unknown): void {
  const q = question.value
  if (!q) return

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      mcqSelection.value = value as number | null
      break
    case 'multi':
      multiSelection.value = value as number[]
      break
    case 'matching':
    case 'enhanced-matching':
      matchingSelection.value = value as number[]
      break
    case 'hotspot':
      hotspotSelection.value = value as string[]
      break
    case 'pulldown':
      pulldownSelection.value = value as Record<string, number>
      break
  }
}

function onStrikeUpdate(next: Set<number>): void {
  const q = question.value
  if (!q) return
  strikeThroughs.value.set(q.id, next)
}

function updateTimerDisplay(): void {
  timeRemaining.value = session.getTimeRemaining()
  timeElapsed.value = session.getTimeElapsed()
}

function startTimerTick(): void {
  updateTimerDisplay()
  timerTickInterval = setInterval(updateTimerDisplay, 1000)
}

function toggleFlag(): void {
  const q = question.value
  if (!q) return
  session.toggleFlag(q.id)
}

function normalizeId(id: string): string {
  return id.replace(/__dup\d+$/, '').replace(/__fill\d+$/, '')
}

const isBookmarked = computed(() => {
  const q = question.value
  if (!q) return false
  return bookmarkedIds.value.has(normalizeId(q.id))
})

async function toggleBookmark(): Promise<void> {
  const q = question.value
  if (!q) return
  const baseId = normalizeId(q.id)
  if (bookmarkedIds.value.has(baseId)) {
    await db.bookmarks.delete(baseId)
    bookmarkedIds.value.delete(baseId)
  } else {
    await db.bookmarks.put({ questionId: baseId, savedAt: Date.now() })
    bookmarkedIds.value.add(baseId)
  }
  bookmarkedIds.value = new Set(bookmarkedIds.value)
}

async function confirmQuit(): Promise<void> {
  if (!window.confirm(t('exam.quitConfirm'))) return
  await session.quit()
  router.push(`/results/${session.attemptId || 'latest'}`)
}

async function confirmSubmit(): Promise<void> {
  if (!window.confirm(t('exam.submitConfirm'))) return
  if (!window.confirm(t('exam.submitConfirm2'))) return
  await session.submit()
  router.push(`/results/${session.attemptId}`)
}

function handleNext(): void {
  if (session.isLast && isRealExam.value) {
    session.enterSectionReview()
    return
  }
  const moved = session.next()
  if (!moved && isRealExam.value && session.state === 'reviewingSection') {
    return
  }
}

function handleStartBreak(): void {
  session.startBreak()
}

function handleResumeBreak(): void {
  session.resumeFromBreak()
}

function handleSkipBreak(): void {
  session.skipBreak()
}

function onTimeWarning(minutes: number): void {
  if (typeof navigator !== 'undefined' && navigator.vibrate) {
    navigator.vibrate(200)
  }
  // Toast could be added later; for now console is sufficient in dev
  void minutes
}

function onBeforeUnload(e: BeforeUnloadEvent): void {
  if (session.isInProgress) {
    e.preventDefault()
    e.returnValue = ''
  }
}

async function requestFullscreen(): Promise<void> {
  try {
    await document.documentElement.requestFullscreen?.()
  } catch {
    // Not supported or denied
  }
}

async function requestWakeLock(): Promise<void> {
  try {
    if ('wakeLock' in navigator) {
      wakeLock = await navigator.wakeLock.request('screen')
    }
  } catch {
    // Not supported or denied
  }
}

async function checkResume(): Promise<boolean> {
  const snapshot = await session.findInProgressAttempt()
  if (!snapshot) return false
  showResumePrompt.value = true
  return true
}

async function handleResumeYes(): Promise<void> {
  const snapshot = await session.findInProgressAttempt()
  if (snapshot) {
    await session.resumeSession(snapshot)
    showResumePrompt.value = false
    resumeChecked.value = true
    startTimerTick()
    await requestWakeLock()
  }
}

async function handleResumeNo(): Promise<void> {
  await session.discardInProgress()
  showResumePrompt.value = false
  resumeChecked.value = true
  router.replace('/mode')
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  const tag = target.tagName
  return tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA' || target.isContentEditable
}

function onKeydown(e: KeyboardEvent): void {
  if (isEditableTarget(e.target)) return

  if (e.key === 'f' || e.key === 'F') {
    e.preventDefault()
    toggleFlag()
    return
  }

  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    if (!session.isFirst) session.previous()
    return
  }

  if (e.key === 'ArrowRight') {
    e.preventDefault()
    if (!session.isLast) handleNext()
    return
  }

  const q = question.value
  if (!q || (q.type !== 'mcq' && q.type !== 'graphic-mcq')) return
  if (answerDisabled.value) return

  const num = Number(e.key)
  if (num >= 1 && num <= 4 && num <= q.options.length) {
    e.preventDefault()
    mcqSelection.value = num - 1
  }
}

watch(
  () => session.currentIndex,
  () => loadLocalSelection(),
  { immediate: true },
)

watch(
  () => question.value?.id,
  (id) => {
    if (id) ai.switchQuestion(id)
  },
  { immediate: true },
)

watch(mcqSelection, (val) => {
  const q = question.value
  if (!q || (q.type !== 'mcq' && q.type !== 'graphic-mcq')) return
  if (val === null) return
  session.answer(q.id, val)
})

watch(
  multiSelection,
  (val) => {
    const q = question.value
    if (!q || q.type !== 'multi') return
    if (val.length !== q.selectN) return
    session.answer(q.id, val)
  },
  { deep: true },
)

watch(
  matchingSelection,
  (val) => {
    const q = question.value
    if (!q || (q.type !== 'matching' && q.type !== 'enhanced-matching')) return
    if (val.length !== q.left.length) return
    session.answer(q.id, val)
  },
  { deep: true },
)

watch(
  hotspotSelection,
  (val) => {
    const q = question.value
    if (!q || q.type !== 'hotspot') return
    if (val.length === 0) return
    session.answer(q.id, val)
  },
  { deep: true },
)

watch(
  pulldownSelection,
  (val) => {
    const q = question.value
    if (!q || q.type !== 'pulldown') return
    if (!isPulldownComplete(q, val)) return
    session.answer(q.id, val)
  },
  { deep: true },
)

watch(
  () => session.state,
  (newState) => {
    if (newState === 'scored' || newState === 'quit') {
      router.push(`/results/${session.attemptId}`)
    }
  },
)

onMounted(async () => {
  if (!session.isInProgress && session.state === 'configuring') {
    const hasResume = await checkResume()
    if (hasResume) return
    router.replace('/mode')
    return
  }

  resumeChecked.value = true

  const bookmarks = await db.bookmarks.toArray()
  bookmarkedIds.value = new Set(bookmarks.map((b) => b.questionId))

  try {
    const cases = await loadAllCases()
    caseMap.value = new Map(cases.map((c) => [c.id, c]))
  } catch {
    // Cases optional until bank includes caseId references
  }

  startTimerTick()
  await requestFullscreen()
  await requestWakeLock()

  window.addEventListener('keydown', onKeydown)
  window.addEventListener('beforeunload', onBeforeUnload)
})

onUnmounted(() => {
  if (timerTickInterval) clearInterval(timerTickInterval)
  wakeLock?.release().catch(() => {})
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('beforeunload', onBeforeUnload)
})
</script>

<template>
  <!-- Resume prompt -->
  <div
    v-if="showResumePrompt"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
  >
    <div class="w-full max-w-md rounded-2xl border border-border bg-surface-raised p-6 shadow-lg">
      <h2 class="mb-2 text-lg font-bold text-on-surface">{{ t('exam.resume') }}</h2>
      <p class="mb-6 text-sm text-on-surface-muted">{{ t('exam.resumePrompt') }}</p>
      <div class="flex gap-3">
        <button
          type="button"
          class="min-h-[44px] flex-1 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
          @click="handleResumeYes"
        >
          {{ t('exam.resumeYes') }}
        </button>
        <button
          type="button"
          class="min-h-[44px] flex-1 rounded-xl border border-border px-4 py-2 text-sm font-semibold text-on-surface"
          @click="handleResumeNo"
        >
          {{ t('exam.resumeNo') }}
        </button>
      </div>
    </div>
  </div>

  <!-- Break screen -->
  <BreakScreen
    v-else-if="isOnBreak"
    :break-duration="EXAM.BREAK_DURATION_MINUTES * 60"
    :break-number="breakNumber"
    @resume="handleResumeBreak"
    @skip="handleSkipBreak"
  />

  <!-- Section review -->
  <SectionReviewScreen
    v-else-if="isSectionReview"
    :questions="sectionReviewQuestions"
    :section-label="sectionLabelText"
    :current-index="session.currentIndex"
    @go-to-question="session.goTo"
    @start-break="handleStartBreak"
  />

  <!-- Main exam room -->
  <div
    v-else-if="question && resumeChecked"
    class="mx-auto flex min-h-[calc(100vh-8rem)] max-w-5xl flex-col px-4 pb-28 pt-4"
  >
    <TimerBar
      :time-remaining="timeRemaining"
      :time-elapsed="timeElapsed"
      :timer-mode="session.config?.timerMode ?? 'off'"
      :question-index="session.currentIndex"
      :total-questions="session.totalQuestions"
      :section-label="sectionLabelText"
      :is-flagged="session.isFlagged(question.id)"
      :timer-visible="session.timerVisible"
      @toggle-flag="toggleFlag"
      @toggle-timer-visible="session.toggleTimerVisible()"
      @time-warning="onTimeWarning"
    />

    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <div class="flex gap-2">
        <button
          type="button"
          class="touch-target rounded-xl border border-border bg-surface-raised px-4 py-2 text-sm font-medium text-on-surface transition hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          :aria-label="t('exam.calculator')"
          @click="showCalculator = true"
        >
          {{ t('exam.calculator') }}
        </button>
        <button
          type="button"
          class="touch-target rounded-xl border border-border bg-surface-raised px-4 py-2 text-sm font-medium text-on-surface transition hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          :class="isBookmarked ? 'border-warning text-warning' : ''"
          :aria-label="isBookmarked ? t('srs.unbookmark') : t('srs.bookmark')"
          @click="toggleBookmark"
        >
          {{ isBookmarked ? '🔖' : '📑' }}
        </button>
        <button
          type="button"
          class="touch-target rounded-xl border border-border bg-surface-raised px-4 py-2 text-sm font-medium text-on-surface transition hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          :aria-label="t('exam.scratchPad')"
          @click="showScratchPad = true"
        >
          {{ t('exam.scratchPad') }}
        </button>
      </div>
      <button
        type="button"
        class="touch-target rounded-xl border border-border px-4 py-2 text-sm font-medium text-danger transition hover:border-danger hover:bg-danger/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-danger"
        @click="confirmQuit"
      >
        {{ t('exam.quit') }}
      </button>
    </div>

    <!-- Question card -->
    <div class="flex-1 rounded-2xl border border-border bg-surface-raised p-5 shadow-sm sm:p-6">
      <LanguagePeek
        v-if="question"
        :question="question"
        :current-lang="lang"
      />

      <CaseSetRenderer
        v-if="currentCase"
        :scenario="currentCase.scenario"
        :current-question-index="caseQuestionIndex"
        :total-questions="caseQuestionTotal"
        :lang="lang"
      >
        <component
          :is="rendererComponent"
          v-if="rendererComponent"
          v-bind="rendererProps"
          @update:model-value="onRendererUpdate"
          @update:strike-throughs="onStrikeUpdate"
        />
      </CaseSetRenderer>

      <component
        :is="rendererComponent"
        v-else-if="rendererComponent"
        v-bind="rendererProps"
        @update:model-value="onRendererUpdate"
        @update:strike-throughs="onStrikeUpdate"
      />

      <div v-else class="py-8 text-center text-on-surface-muted">
        <p>{{ t('common.loading') }}</p>
        <p class="mt-2 text-sm">({{ question.type }})</p>
      </div>

      <div
        v-if="showFeedback && hasAnswer"
        class="mt-6 rounded-xl border border-border bg-surface-alt p-4"
      >
        <div class="mb-2 flex items-center gap-2">
          <span
            class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
            :class="
              session.getAnswer(question.id)?.correct
                ? 'bg-success/15 text-success'
                : 'bg-danger/15 text-danger'
            "
          >
            {{ session.getAnswer(question.id)?.correct ? t('exam.correct') : t('exam.incorrect') }}
          </span>
        </div>
        <h3 class="mb-2 text-sm font-semibold text-on-surface">{{ t('exam.explanation') }}</h3>
        <p class="text-sm leading-relaxed text-on-surface-muted whitespace-pre-wrap">
          {{ ltext(question.explanation) }}
        </p>
      </div>
    </div>

    <Calculator :visible="showCalculator" @close="showCalculator = false" />

    <ScratchPad
      v-if="question"
      :visible="showScratchPad"
      :model-value="getScratchPadNotes(question.id)"
      :question-id="question.id"
      @update:model-value="setScratchPadNotes(question.id, $event)"
      @close="showScratchPad = false"
    />

    <ChatFab
      :visible="showChatFab"
      @toggle="showChatPanel = !showChatPanel"
    />

    <ChatPanel
      :visible="showChatPanel"
      :question-context="questionContext"
      @close="showChatPanel = false"
    />

    <!-- Bottom nav -->
    <div
      class="fixed inset-x-0 bottom-16 z-30 border-t border-border bg-surface/95 px-4 py-3 backdrop-blur"
    >
      <div class="mx-auto flex max-w-5xl gap-3">
        <button
          type="button"
          class="min-h-[44px] flex-1 rounded-xl border border-border bg-surface-raised px-4 py-3 text-sm font-semibold text-on-surface transition hover:border-primary disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="session.isFirst"
          @click="session.previous()"
        >
          {{ t('exam.previous') }}
        </button>

        <button
          v-if="session.isLast && isRealExam"
          type="button"
          class="min-h-[44px] flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark"
          @click="confirmSubmit"
        >
          {{ t('exam.submit') }}
        </button>
        <button
          v-else-if="session.isLast"
          type="button"
          class="min-h-[44px] flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark"
          @click="confirmSubmit"
        >
          {{ t('exam.submit') }}
        </button>
        <button
          v-else
          type="button"
          class="min-h-[44px] flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark"
          @click="handleNext"
        >
          {{ t('exam.next') }}
        </button>
      </div>
    </div>
  </div>

  <div v-else-if="!showResumePrompt" class="mx-auto max-w-5xl px-4 py-12 text-center text-on-surface-muted">
    {{ t('common.loading') }}
  </div>
</template>
