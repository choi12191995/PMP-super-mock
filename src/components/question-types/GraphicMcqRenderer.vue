<script setup lang="ts">
import McqRenderer from '@/components/question-types/McqRenderer.vue'
import type { McqQ } from '@/core/types'

defineProps<{
  question: McqQ
  modelValue: number | null
  showFeedback: boolean
  correctAnswer: number
  disabled: boolean
  strikeThroughs: Set<number>
  lang: 'en' | 'zh-TW'
}>()

defineEmits<{
  'update:modelValue': [value: number | null]
  'update:strikeThroughs': [value: Set<number>]
}>()
</script>

<template>
  <div class="space-y-5">
    <div
      v-if="question.media"
      class="overflow-hidden rounded-xl border border-border bg-surface-alt p-4"
    >
      <img
        :src="`/questions/media/${question.media}`"
        :alt="question.media"
        class="mx-auto max-h-80 w-full object-contain"
      />
    </div>

    <McqRenderer
      :question="question"
      :model-value="modelValue"
      :show-feedback="showFeedback"
      :correct-answer="correctAnswer"
      :disabled="disabled"
      :strike-throughs="strikeThroughs"
      :lang="lang"
      @update:model-value="$emit('update:modelValue', $event)"
      @update:strike-throughs="$emit('update:strikeThroughs', $event)"
    />
  </div>
</template>
