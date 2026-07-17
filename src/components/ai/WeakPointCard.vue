<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chat } from '@/core/ai/client'
import { buildWeakPointPrompt } from '@/core/ai/prompts'
import { useAiStore } from '@/stores/ai'
import { db } from '@/db/index'
import type { ScoreResult } from '@/core/types'

const props = defineProps<{
  attemptId: string
  score: ScoreResult
  wrongQuestions: { stem: string; chosenAnswer: string; correctAnswer: string }[]
  initialAiSummary?: string | null
}>()

const emit = defineEmits<{
  saved: [summary: string]
}>()

const { t, locale } = useI18n()
const ai = useAiStore()

const aiSummary = ref(props.initialAiSummary ?? '')
const loading = ref(false)
const error = ref<string | null>(null)

const uiLang = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en') as 'en' | 'zh-TW')

const taskStats = computed(() =>
  Object.entries(props.score.byTask)
    .filter(([, s]) => s.total > 0)
    .map(([task, s]) => ({ task, accuracy: s.correct / s.total }))
    .sort((a, b) => a.accuracy - b.accuracy),
)

const domainStats = computed(() =>
  Object.entries(props.score.byDomain)
    .filter(([, s]) => s.total > 0)
    .map(([domain, s]) => ({ domain, accuracy: s.correct / s.total }))
    .sort((a, b) => a.accuracy - b.accuracy),
)

const typeStats = computed(() =>
  Object.entries(props.score.byType)
    .filter(([, s]) => s.total > 0)
    .map(([type, s]) => ({ type, accuracy: s.correct / s.total }))
    .sort((a, b) => a.accuracy - b.accuracy),
)

function domainLabel(domain: string): string {
  const map: Record<string, string> = {
    people: t('common.people'),
    process: t('common.process'),
    business: t('common.business'),
  }
  return map[domain] ?? domain
}

const localSummaryParts = computed(() => {
  const parts: string[] = []
  const weakestDomain = domainStats.value[0]
  const weakestTask = taskStats.value[0]
  const weakestType = typeStats.value[0]

  if (weakestDomain) {
    parts.push(`${domainLabel(weakestDomain.domain)} (${Math.round(weakestDomain.accuracy * 100)}%)`)
  }
  if (weakestTask) {
    parts.push(`${weakestTask.task} (${Math.round(weakestTask.accuracy * 100)}%)`)
  }
  if (weakestType) {
    parts.push(`${weakestType.type} (${Math.round(weakestType.accuracy * 100)}%)`)
  }
  return parts
})

const renderedAiSummary = computed(() => {
  if (!aiSummary.value) return ''
  const raw = marked.parse(aiSummary.value, { async: false }) as string
  return DOMPurify.sanitize(raw)
})

async function generateStudyPlan(): Promise<void> {
  if (!ai.isConfigured || !ai.enabled) return

  loading.value = true
  error.value = null

  try {
    const lang = ai.resolveLanguage(uiLang.value)
    const messages = buildWeakPointPrompt({
      stats: taskStats.value,
      wrongQuestions: props.wrongQuestions,
      language: lang,
    })
    const result = await chat(ai.aiConfig, messages)
    aiSummary.value = result

    const attempt = await db.attempts.get(props.attemptId)
    if (attempt) {
      await db.attempts.put({
        ...attempt,
        aiSummary: result,
      })
    }
    emit('saved', result)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to generate'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="rounded-2xl border border-border bg-surface-raised p-5">
    <h2 class="mb-4 text-lg font-semibold text-on-surface">
      {{ t('results.weakSummary') }}
    </h2>

    <div class="mb-4 rounded-xl bg-surface-alt p-4">
      <p class="mb-2 text-sm font-medium text-on-surface">{{ t('ai.weakestAreas') }}</p>
      <p class="text-sm text-on-surface-muted">
        <template v-if="localSummaryParts.length">
          {{ localSummaryParts.join(' · ') }}
        </template>
        <template v-else>{{ t('common.noData') }}</template>
      </p>
    </div>

    <div v-if="ai.isConfigured && ai.enabled">
      <button
        v-if="!aiSummary && !loading"
        type="button"
        class="w-full rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-50"
        @click="generateStudyPlan"
      >
        {{ t('ai.getStudyPlan') }}
      </button>

      <p v-if="loading" class="text-sm text-on-surface-muted">{{ t('ai.generating') }}</p>

      <div
        v-if="error"
        class="mt-3 rounded-xl border border-danger/30 bg-danger/10 p-3 text-sm text-danger"
      >
        {{ t('ai.error', { msg: error }) }}
        <button
          type="button"
          class="ml-2 font-medium underline"
          @click="generateStudyPlan"
        >
          {{ t('ai.retry') }}
        </button>
      </div>

      <div
        v-if="aiSummary"
        class="prose prose-sm mt-4 max-w-none text-on-surface dark:prose-invert"
        v-html="renderedAiSummary"
      />
    </div>

    <p
      v-else-if="!ai.isConfigured"
      class="text-sm text-on-surface-muted"
    >
      {{ t('ai.notConfigured') }}
    </p>
  </section>
</template>
