<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { optionDisplayOrder } from '@/core/shuffleOptions'
import type {
  Question,
  LText,
  McqQ,
  MultiQ,
  MatchingQ,
  PulldownQ,
} from '@/core/types'

const props = defineProps<{
  question: Question
  currentLang: 'en' | 'zh-TW'
  sessionSeed?: number
}>()

const { t } = useI18n()
const expanded = ref(false)

const otherLang = computed(() => (props.currentLang === 'en' ? 'zh-TW' : 'en'))

const toggleLabel = computed(() => (props.currentLang === 'en' ? '中' : 'EN'))

function ltext(text: LText): string {
  return otherLang.value === 'zh-TW' ? text.zh : text.en
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
}

const displayOrder = computed(() => {
  const q = props.question
  if (q.type !== 'mcq' && q.type !== 'graphic-mcq' && q.type !== 'multi') return null
  return optionDisplayOrder(q.id, (q as McqQ | MultiQ).options.length, props.sessionSeed ?? 0)
})

const mcqOptions = computed(() => {
  if (props.question.type !== 'mcq' && props.question.type !== 'graphic-mcq' && props.question.type !== 'multi') {
    return null
  }
  const original = (props.question as McqQ | MultiQ).options
  if (!displayOrder.value) return original
  return displayOrder.value.map((origIdx) => original[origIdx])
})

const matchingItems = computed(() => {
  if (props.question.type !== 'matching' && props.question.type !== 'enhanced-matching') {
    return null
  }
  const q = props.question as MatchingQ
  return { left: q.left, right: q.right }
})

const pulldownBlanks = computed(() => {
  if (props.question.type !== 'pulldown') return null
  return (props.question as PulldownQ).blanks
})

function toggle(): void {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="mb-4">
    <button
      type="button"
      class="touch-target inline-flex min-h-[44px] items-center gap-1.5 rounded-lg border border-border bg-surface-alt px-3 py-1.5 text-xs font-semibold text-on-surface-muted transition hover:border-primary hover:text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
      :aria-expanded="expanded"
      :aria-controls="`lang-peek-${question.id}`"
      @click="toggle"
    >
      <span aria-hidden="true">{{ toggleLabel }}</span>
      <span class="sr-only">{{ t('exam.languagePeek') }}</span>
    </button>

    <div
      v-if="expanded"
      :id="`lang-peek-${question.id}`"
      class="mt-3 rounded-xl border border-dashed border-primary/40 bg-primary/5 p-4"
    >
      <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-primary">
        {{ t('exam.languagePeekLabel', { lang: toggleLabel }) }}
      </p>

      <p class="text-sm leading-relaxed text-on-surface whitespace-pre-wrap">
        {{ ltext(question.stem) }}
      </p>

      <ul v-if="mcqOptions" class="mt-3 space-y-2">
        <li
          v-for="(option, index) in mcqOptions"
          :key="index"
          class="text-sm leading-relaxed text-on-surface"
        >
          <span class="mr-2 font-semibold text-on-surface-muted">{{ optionLabel(index) }}.</span>
          {{ ltext(option) }}
        </li>
      </ul>

      <div v-else-if="matchingItems" class="mt-3 grid gap-4 sm:grid-cols-2">
        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-on-surface-muted">
            {{ t('exam.leftColumn') }}
          </p>
          <ul class="space-y-1">
            <li
              v-for="(item, index) in matchingItems.left"
              :key="'l-' + index"
              class="text-sm text-on-surface"
            >
              {{ index + 1 }}. {{ ltext(item) }}
            </li>
          </ul>
        </div>
        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-on-surface-muted">
            {{ t('exam.rightColumn') }}
          </p>
          <ul class="space-y-1">
            <li
              v-for="(item, index) in matchingItems.right"
              :key="'r-' + index"
              class="text-sm text-on-surface"
            >
              {{ String.fromCharCode(65 + index) }}. {{ ltext(item) }}
            </li>
          </ul>
        </div>
      </div>

      <div v-else-if="pulldownBlanks" class="mt-3 space-y-3">
        <div v-for="blank in pulldownBlanks" :key="blank.id">
          <p class="mb-1 text-xs font-medium text-on-surface-muted">{{ blank.id }}</p>
          <ul class="space-y-1">
            <li
              v-for="(option, index) in blank.options"
              :key="index"
              class="text-sm text-on-surface"
            >
              {{ index + 1 }}. {{ ltext(option) }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
