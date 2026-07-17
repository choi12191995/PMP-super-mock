<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import NavigatorPalette from './NavigatorPalette.vue'

export interface SectionQuestionStatus {
  index: number
  answered: boolean
  flagged: boolean
}

const props = defineProps<{
  questions: SectionQuestionStatus[]
  sectionLabel: string
  currentIndex: number
}>()

const emit = defineEmits<{
  'go-to-question': [index: number]
  'start-break': []
}>()

const { t } = useI18n()

const total = computed(() => props.questions.length)

const answeredSet = computed(() => {
  const set = new Set<number>()
  for (const q of props.questions) {
    if (q.answered) set.add(q.index)
  }
  return set
})

const flaggedSet = computed(() => {
  const set = new Set<number>()
  for (const q of props.questions) {
    if (q.flagged) set.add(q.index)
  }
  return set
})
</script>

<template>
  <div class="mx-auto flex min-h-[calc(100vh-8rem)] max-w-2xl flex-col px-4 py-8">
    <div class="glass-card p-6">
      <h1 class="mb-1 text-xl font-bold text-on-surface">{{ t('exam.sectionReview') }}</h1>
      <p v-if="sectionLabel" class="mb-4 text-sm text-on-surface-muted">{{ sectionLabel }}</p>

      <NavigatorPalette
        :total="total"
        :current="questions.findIndex((q) => q.index === currentIndex)"
        :answered-set="answeredSet"
        :flagged-set="flaggedSet"
        :index-map="questions.map((q) => q.index)"
        @navigate="(localIdx) => emit('go-to-question', questions[localIdx]?.index ?? localIdx)"
      />

      <div class="mt-4 flex flex-wrap gap-4 text-xs text-on-surface-muted">
        <span class="flex items-center gap-1.5">
          <span class="inline-block h-3 w-3 rounded bg-success" />
          {{ t('exam.answered') }}
        </span>
        <span class="flex items-center gap-1.5">
          <span class="inline-block h-3 w-3 rounded border-2 border-border" />
          {{ t('exam.unanswered') }}
        </span>
        <span class="flex items-center gap-1.5">
          <span class="text-warning">▲</span>
          {{ t('exam.flagged') }}
        </span>
      </div>

      <p class="mt-6 rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
        {{ t('exam.sectionLock') }}
      </p>

      <button
        type="button"
        class="mt-6 w-full min-h-[48px] rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark"
        @click="emit('start-break')"
      >
        {{ t('exam.startBreak') }}
      </button>
    </div>
  </div>
</template>
