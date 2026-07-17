<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db, type AttemptRecord, type AnswerRecord } from '@/db/index'
import { loadAllQuestions } from '@/core/bank/loader'
import type { LText, Question } from '@/core/types'
import McqRenderer from '@/components/question-types/McqRenderer.vue'
import MultiRenderer from '@/components/question-types/MultiRenderer.vue'
import MatchingRenderer from '@/components/question-types/MatchingRenderer.vue'
import HotspotRenderer from '@/components/question-types/HotspotRenderer.vue'
import PulldownRenderer from '@/components/question-types/PulldownRenderer.vue'
import GraphicMcqRenderer from '@/components/question-types/GraphicMcqRenderer.vue'

const route = useRoute()
const { t, locale } = useI18n()

const attempt = ref<AttemptRecord | null>(null)
const answers = ref<AnswerRecord[]>([])
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const loading = ref(true)

const attemptId = computed(() => route.params.attemptId as string)
const lang = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en') as 'en' | 'zh-TW')

const reviewSessionSeed = computed(() => {
  const seed = attempt.value?.config?.seed
  return typeof seed === 'number' ? seed : 0
})

const currentAnswer = computed(() => answers.value[currentIndex.value] ?? null)
const currentQuestion = computed(() => {
  const ans = currentAnswer.value
  if (!ans) return null
  return questions.value.find((q) => q.id === ans.questionId) ?? null
})

const total = computed(() => answers.value.length)
const isFirst = computed(() => currentIndex.value === 0)
const isLast = computed(() => currentIndex.value >= total.value - 1)

onMounted(async () => {
  try {
    const [att, ans, allQuestions] = await Promise.all([
      db.attempts.get(attemptId.value),
      db.answers.where('attemptId').equals(attemptId.value).toArray(),
      loadAllQuestions(),
    ])

    attempt.value = att ?? null
    const qMap = new Map(allQuestions.map((q) => [q.id, q]))
    answers.value = ans.sort((a, b) => a.answeredAt - b.answeredAt)
    questions.value = answers.value
      .map((a) => qMap.get(a.questionId))
      .filter((q): q is Question => q != null)
  } finally {
    loading.value = false
  }
})

function ltext(text: LText): string {
  return lang.value === 'zh-TW' ? text.zh : text.en
}

function previous(): void {
  if (!isFirst.value) currentIndex.value -= 1
}

function next(): void {
  if (!isLast.value) currentIndex.value += 1
}

function givenValue(): unknown {
  return currentAnswer.value?.given ?? null
}

function mcqGiven(): number | null {
  const v = givenValue()
  return typeof v === 'number' ? v : null
}

function multiGiven(): number[] {
  const v = givenValue()
  return Array.isArray(v) ? (v as number[]) : []
}

function matchingGiven(): number[] {
  const v = givenValue()
  return Array.isArray(v) ? (v as number[]) : []
}

function hotspotGiven(): string[] {
  const v = givenValue()
  return Array.isArray(v) ? (v as string[]) : []
}

function pulldownGiven(): Record<string, number> {
  const v = givenValue()
  if (typeof v === 'object' && v !== null) return v as Record<string, number>
  return {}
}

function correctMcq(q: Question): number {
  if (q.type === 'mcq' || q.type === 'graphic-mcq') return q.correct
  return 0
}

function correctMulti(q: Question): number[] {
  if (q.type === 'multi') return q.correct
  return []
}

function correctMatching(q: Question): number[] {
  if (q.type === 'matching' || q.type === 'enhanced-matching') return q.correct
  return []
}

function correctHotspot(q: Question): string[] {
  if (q.type === 'hotspot') return q.correct
  return []
}

function correctPulldown(q: Question): Record<string, number> {
  if (q.type !== 'pulldown') return {}
  const result: Record<string, number> = {}
  for (const blank of q.blanks) {
    result[blank.id] = blank.correct
  }
  return result
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-4 text-2xl font-bold text-on-surface">{{ t('results.reviewAnswers') }}</h1>

    <p v-if="loading" class="text-on-surface-muted">{{ t('common.loading') }}</p>

    <template v-else-if="currentQuestion && currentAnswer">
      <!-- Progress -->
      <div class="mb-4 flex items-center justify-between text-sm text-on-surface-muted">
        <span>{{ t('exam.question') }} {{ currentIndex + 1 }} {{ t('exam.of') }} {{ total }}</span>
        <span
          class="rounded-full px-3 py-0.5 text-xs font-semibold"
          :class="
            currentAnswer.correct
              ? 'bg-success/15 text-success'
              : 'bg-danger/15 text-danger'
          "
        >
          {{ currentAnswer.correct ? t('exam.correct') : t('exam.incorrect') }}
        </span>
      </div>

      <!-- Question -->
      <div class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <McqRenderer
          v-if="currentQuestion.type === 'mcq'"
          :question="currentQuestion"
          :model-value="mcqGiven()"
          :show-feedback="true"
          :correct-answer="correctMcq(currentQuestion)"
          :disabled="true"
          :strike-throughs="new Set()"
          :lang="lang"
          :session-seed="reviewSessionSeed"
        />
        <GraphicMcqRenderer
          v-else-if="currentQuestion.type === 'graphic-mcq'"
          :question="currentQuestion"
          :model-value="mcqGiven()"
          :show-feedback="true"
          :correct-answer="correctMcq(currentQuestion)"
          :disabled="true"
          :strike-throughs="new Set()"
          :lang="lang"
          :session-seed="reviewSessionSeed"
        />
        <MultiRenderer
          v-else-if="currentQuestion.type === 'multi'"
          :question="currentQuestion"
          :model-value="multiGiven()"
          :show-feedback="true"
          :correct-answer="correctMulti(currentQuestion)"
          :disabled="true"
          :strike-throughs="new Set()"
          :lang="lang"
          :session-seed="reviewSessionSeed"
        />
        <MatchingRenderer
          v-else-if="currentQuestion.type === 'matching' || currentQuestion.type === 'enhanced-matching'"
          :question="currentQuestion"
          :model-value="matchingGiven()"
          :show-feedback="true"
          :correct-answer="correctMatching(currentQuestion)"
          :disabled="true"
          :lang="lang"
        />
        <HotspotRenderer
          v-else-if="currentQuestion.type === 'hotspot'"
          :question="currentQuestion"
          :model-value="hotspotGiven()"
          :show-feedback="true"
          :correct-answer="correctHotspot(currentQuestion)"
          :disabled="true"
          :lang="lang"
        />
        <PulldownRenderer
          v-else-if="currentQuestion.type === 'pulldown'"
          :question="currentQuestion"
          :model-value="pulldownGiven()"
          :show-feedback="true"
          :correct-answer="correctPulldown(currentQuestion)"
          :disabled="true"
          :lang="lang"
        />
      </div>

      <!-- Explanation -->
      <div class="mb-6 rounded-2xl border border-border bg-surface-alt p-5">
        <h2 class="mb-2 text-sm font-semibold uppercase tracking-wide text-on-surface-muted">
          {{ t('exam.explanation') }}
        </h2>
        <p class="whitespace-pre-wrap text-sm leading-relaxed text-on-surface">
          {{ ltext(currentQuestion.explanation) }}
        </p>
      </div>

      <!-- Navigation -->
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 rounded-xl border border-border bg-surface-raised px-4 py-3 font-medium text-on-surface transition hover:bg-surface-alt disabled:opacity-40"
          :disabled="isFirst"
          @click="previous"
        >
          {{ t('exam.previous') }}
        </button>
        <button
          type="button"
          class="flex-1 rounded-xl bg-primary px-4 py-3 font-medium text-white transition hover:bg-primary-dark disabled:opacity-40"
          :disabled="isLast"
          @click="next"
        >
          {{ t('exam.next') }}
        </button>
      </div>
    </template>

    <p v-else class="text-on-surface-muted">{{ t('history.empty') }}</p>
  </div>
</template>
