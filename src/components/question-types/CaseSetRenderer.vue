<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import type { LText } from '@/core/types'

const props = defineProps<{
  scenario: LText
  currentQuestionIndex: number
  totalQuestions: number
  lang: 'en' | 'zh-TW'
}>()

const { t } = useI18n()
const mobileTab = ref<'scenario' | 'question'>('question')
const scenarioCollapsed = ref(false)

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

const renderedScenario = computed(() => {
  const raw = marked.parse(ltext(props.scenario), { async: false }) as string
  return DOMPurify.sanitize(raw)
})

const headerText = computed(() =>
  t('exam.caseStudyHeader', {
    current: props.currentQuestionIndex + 1,
    total: props.totalQuestions,
  }),
)
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-sm font-semibold text-on-surface-muted">
      {{ headerText }}
    </h2>

    <!-- Mobile: tab interface -->
    <div class="md:hidden">
      <div class="mb-4 flex rounded-xl border border-border bg-surface-alt p-1">
        <button
          type="button"
          class="min-h-[44px] flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition touch-manipulation"
          :class="
            mobileTab === 'scenario'
              ? 'bg-surface-raised text-primary shadow-sm'
              : 'text-on-surface-muted'
          "
          @click="mobileTab = 'scenario'"
        >
          {{ t('exam.scenario') }}
        </button>
        <button
          type="button"
          class="min-h-[44px] flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition touch-manipulation"
          :class="
            mobileTab === 'question'
              ? 'bg-surface-raised text-primary shadow-sm'
              : 'text-on-surface-muted'
          "
          @click="mobileTab = 'question'"
        >
          {{ t('exam.question') }}
        </button>
      </div>

      <div
        v-show="mobileTab === 'scenario'"
        class="prose prose-sm max-w-none rounded-xl border border-border bg-surface-alt p-4 text-on-surface"
        v-html="renderedScenario"
      />

      <div v-show="mobileTab === 'question'">
        <slot />
      </div>
    </div>

    <!-- Desktop: side-by-side -->
    <div class="hidden gap-6 md:grid md:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <div class="min-w-0">
        <button
          type="button"
          class="mb-2 flex min-h-[44px] w-full items-center justify-between rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm font-semibold text-on-surface transition hover:border-primary/50"
          @click="scenarioCollapsed = !scenarioCollapsed"
        >
          <span>{{ t('exam.scenario') }}</span>
          <span class="text-on-surface-muted">{{ scenarioCollapsed ? '▸' : '▾' }}</span>
        </button>

        <div
          v-show="!scenarioCollapsed"
          class="prose prose-sm max-h-[60vh] max-w-none overflow-y-auto rounded-xl border border-border bg-surface-alt p-4 text-on-surface"
          v-html="renderedScenario"
        />
      </div>

      <div class="min-w-0">
        <slot />
      </div>
    </div>
  </div>
</template>
