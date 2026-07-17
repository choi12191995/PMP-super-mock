<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import McqRenderer from '@/components/question-types/McqRenderer.vue'
import MultiRenderer from '@/components/question-types/MultiRenderer.vue'
import { useExamSessionStore } from '@/stores/examSession'
import type { McqQ, MultiQ, LText } from '@/core/types'

const router = useRouter()
const { t, locale } = useI18n()
const session = useExamSessionStore()

const strikeThroughs = ref(new Map<string, Set<number>>())
const mcqSelection = ref<number | null>(null)
const multiSelection = ref<number[]>([])

const lang = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en') as 'en' | 'zh-TW')

const question = computed(() => session.currentQuestion)

const currentStrikes = computed(() => {
  const q = question.value
  if (!q) return new Set<number>()
  return strikeThroughs.value.get(q.id) ?? new Set<number>()
})

const hasAnswer = computed(() => {
  const q = question.value
  if (!q) return false
  const stored = session.getAnswer(q.id)
  if (stored?.given != null) return true
  if (q.type === 'mcq' || q.type === 'graphic-mcq') return mcqSelection.value !== null
  if (q.type === 'multi') return multiSelection.value.length === q.selectN
  return false
})

const showFeedback = computed(() => {
  if (!session.config || session.config.feedbackMode !== 'immediate') return false
  const q = question.value
  if (!q) return false
  if (q.type === 'multi') return multiSelection.value.length === q.selectN
  return mcqSelection.value !== null
})

const answerDisabled = computed(() => showFeedback.value)

function ltext(text: LText): string {
  return lang.value === 'zh-TW' ? text.zh : text.en
}

function loadLocalSelection(): void {
  const q = question.value
  if (!q) return

  const stored = session.getAnswer(q.id)
  if (q.type === 'mcq' || q.type === 'graphic-mcq') {
    mcqSelection.value =
      typeof stored?.given === 'number' ? stored.given : null
  } else if (q.type === 'multi') {
    multiSelection.value = Array.isArray(stored?.given)
      ? [...(stored.given as number[])].sort((a, b) => a - b)
      : []
  }
}

watch(
  () => session.currentIndex,
  () => loadLocalSelection(),
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

function updateStrikes(next: Set<number>): void {
  const q = question.value
  if (!q) return
  strikeThroughs.value.set(q.id, next)
}

function toggleFlag(): void {
  const q = question.value
  if (!q) return
  session.toggleFlag(q.id)
}

function confirmQuit(): void {
  if (!window.confirm(t('exam.quitConfirm'))) return
  session.quit()
  router.push(`/results/${session.attemptId || 'latest'}`)
}

onMounted(() => {
  if (!session.isInProgress && session.state === 'configuring') {
    router.replace('/mode')
  }
})
</script>

<template>
  <div v-if="question" class="mx-auto flex min-h-[calc(100vh-8rem)] max-w-5xl flex-col px-4 pb-28 pt-4">
    <!-- Top bar -->
    <div
      class="mb-4 flex items-center justify-between gap-3 rounded-2xl border border-border bg-surface-raised px-4 py-3 shadow-sm"
    >
      <div class="min-w-0">
        <p class="text-xs font-medium uppercase tracking-wide text-on-surface-muted">
          {{ t('exam.question') }}
        </p>
        <p class="text-lg font-bold text-on-surface">
          {{ session.currentIndex + 1 }}
          <span class="font-normal text-on-surface-muted">{{ t('exam.of') }}</span>
          {{ session.totalQuestions }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="flex min-h-[44px] min-w-[44px] items-center justify-center rounded-xl border border-border px-3 transition hover:border-primary"
          :class="session.isFlagged(question.id) ? 'border-warning bg-warning/10 text-warning' : 'text-on-surface-muted'"
          @click="toggleFlag"
        >
          <span class="text-lg">{{ session.isFlagged(question.id) ? '🚩' : '⚑' }}</span>
          <span class="sr-only">
            {{ session.isFlagged(question.id) ? t('exam.unflag') : t('exam.flag') }}
          </span>
        </button>

        <button
          type="button"
          class="rounded-xl border border-border px-4 py-2.5 text-sm font-medium text-danger transition hover:border-danger hover:bg-danger/5"
          @click="confirmQuit"
        >
          {{ t('exam.quit') }}
        </button>
      </div>
    </div>

    <!-- Question card -->
    <div class="flex-1 rounded-2xl border border-border bg-surface-raised p-5 shadow-sm sm:p-6">
      <McqRenderer
        v-if="question.type === 'mcq' || question.type === 'graphic-mcq'"
        :question="question as McqQ"
        :model-value="mcqSelection"
        :show-feedback="showFeedback"
        :correct-answer="(question as McqQ).correct"
        :disabled="answerDisabled"
        :strike-throughs="currentStrikes"
        :lang="lang"
        @update:model-value="mcqSelection = $event"
        @update:strike-throughs="updateStrikes"
      />

      <MultiRenderer
        v-else-if="question.type === 'multi'"
        :question="question as MultiQ"
        :model-value="multiSelection"
        :show-feedback="showFeedback"
        :correct-answer="(question as MultiQ).correct"
        :disabled="answerDisabled"
        :strike-throughs="currentStrikes"
        :lang="lang"
        @update:model-value="multiSelection = $event"
        @update:strike-throughs="updateStrikes"
      />

      <div v-else class="py-8 text-center text-on-surface-muted">
        <p>{{ t('common.loading') }}</p>
        <p class="mt-2 text-sm">({{ question.type }})</p>
      </div>

      <!-- Immediate feedback explanation -->
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
            {{
              session.getAnswer(question.id)?.correct ? t('exam.correct') : t('exam.incorrect')
            }}
          </span>
        </div>
        <h3 class="mb-2 text-sm font-semibold text-on-surface">{{ t('exam.explanation') }}</h3>
        <p class="text-sm leading-relaxed text-on-surface-muted whitespace-pre-wrap">
          {{ ltext(question.explanation) }}
        </p>
      </div>
    </div>

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
          type="button"
          class="min-h-[44px] flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="session.isLast"
          @click="session.next()"
        >
          {{ t('exam.next') }}
        </button>
      </div>
    </div>
  </div>

  <div v-else class="mx-auto max-w-5xl px-4 py-12 text-center text-on-surface-muted">
    {{ t('common.loading') }}
  </div>
</template>
