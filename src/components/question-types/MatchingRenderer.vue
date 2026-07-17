<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MatchingQ, LText } from '@/core/types'

const props = defineProps<{
  question: MatchingQ
  modelValue: number[]
  showFeedback: boolean
  correctAnswer: number[]
  disabled: boolean
  lang: 'en' | 'zh-TW'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const { t } = useI18n()
const selectedLeft = ref<number | null>(null)

const matches = ref<number[]>([])

watch(
  () => props.modelValue,
  (val) => {
    if (val.length === props.question.left.length) {
      matches.value = [...val]
    } else {
      matches.value = props.question.left.map((_, i) => val[i] ?? -1)
    }
  },
  { immediate: true },
)

const allMatched = computed(() =>
  matches.value.every((m) => m >= 0),
)

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function rightIndexForLeft(leftIndex: number): number {
  return matches.value[leftIndex] ?? -1
}

function leftIndexForRight(rightIndex: number): number {
  return matches.value.findIndex((m) => m === rightIndex)
}

function matchNumber(leftIndex: number): number | null {
  const matched = rightIndexForLeft(leftIndex)
  return matched >= 0 ? leftIndex + 1 : null
}

function onLeftTap(leftIndex: number): void {
  if (props.disabled) return
  selectedLeft.value = selectedLeft.value === leftIndex ? null : leftIndex
}

function onRightTap(rightIndex: number): void {
  if (props.disabled) return
  if (selectedLeft.value === null) return

  const leftIndex = selectedLeft.value
  const next = [...matches.value]

  const prevLeft = leftIndexForRight(rightIndex)
  if (prevLeft >= 0 && prevLeft !== leftIndex) {
    next[prevLeft] = -1
  }

  next[leftIndex] = rightIndex
  matches.value = next
  selectedLeft.value = null

  if (next.every((m) => m >= 0)) {
    emit('update:modelValue', next)
  }
}

function leftClasses(leftIndex: number): string[] {
  const selected = selectedLeft.value === leftIndex
  const matched = rightIndexForLeft(leftIndex) >= 0
  const isCorrect =
    props.showFeedback && matched && matches.value[leftIndex] === props.correctAnswer[leftIndex]
  const isWrong =
    props.showFeedback && matched && matches.value[leftIndex] !== props.correctAnswer[leftIndex]

  const classes = [
    'relative flex min-h-[44px] w-full items-center gap-2 rounded-xl border-2 px-4 py-3 text-left text-sm transition touch-manipulation sm:text-base',
  ]

  if (isCorrect) classes.push('border-success bg-success/10')
  else if (isWrong) classes.push('border-danger bg-danger/10')
  else if (selected) classes.push('border-primary bg-primary/10 ring-2 ring-primary/30')
  else if (matched) classes.push('border-primary/50 bg-primary/5')
  else classes.push('border-border bg-surface-raised hover:border-primary/50')

  if (props.disabled && !props.showFeedback) classes.push('pointer-events-none opacity-70')

  return classes
}

function rightClasses(rightIndex: number): string[] {
  const matchedLeft = leftIndexForRight(rightIndex)
  const matched = matchedLeft >= 0
  const isCorrect =
    props.showFeedback && matched && matches.value[matchedLeft] === props.correctAnswer[matchedLeft]
  const isWrong =
    props.showFeedback && matched && matches.value[matchedLeft] !== props.correctAnswer[matchedLeft]
  const isTarget = selectedLeft.value !== null

  const classes = [
    'relative flex min-h-[44px] w-full items-center gap-2 rounded-xl border-2 px-4 py-3 text-left text-sm transition touch-manipulation sm:text-base',
  ]

  if (isCorrect) classes.push('border-success bg-success/10')
  else if (isWrong) classes.push('border-danger bg-danger/10')
  else if (isTarget) classes.push('border-primary/50 bg-surface-alt hover:border-primary')
  else if (matched) classes.push('border-primary/50 bg-primary/5')
  else classes.push('border-border bg-surface-raised hover:border-primary/50')

  if (props.disabled && !props.showFeedback) classes.push('pointer-events-none opacity-70')

  return classes
}
</script>

<template>
  <div class="space-y-5">
    <p
      class="inline-flex rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary"
    >
      {{ t('exam.matchInstruction') }}
    </p>

    <p class="text-base leading-relaxed text-on-surface whitespace-pre-wrap">
      {{ ltext(question.stem) }}
    </p>

    <p
      v-if="selectedLeft !== null && !allMatched"
      class="text-sm text-primary"
    >
      {{ lang === 'zh-TW' ? '請點選右側項目完成配對' : 'Tap a right item to complete the match' }}
    </p>

    <div class="grid gap-4 md:grid-cols-2">
      <!-- Left column -->
      <div class="space-y-2">
        <p class="text-xs font-semibold uppercase tracking-wide text-on-surface-muted">
          {{ lang === 'zh-TW' ? '左側' : 'Left' }}
        </p>
        <div class="space-y-2" role="listbox" :aria-label="t('exam.matchInstruction')">
          <button
            v-for="(item, leftIndex) in question.left"
            :key="'left-' + leftIndex"
            type="button"
            role="option"
            :aria-selected="selectedLeft === leftIndex"
            :class="leftClasses(leftIndex)"
            @click="onLeftTap(leftIndex)"
          >
            <span
              v-if="matchNumber(leftIndex)"
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-white"
            >
              {{ matchNumber(leftIndex) }}
            </span>
            <span
              v-else
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 border-border"
            />
            <span class="flex-1 text-on-surface">{{ ltext(item) }}</span>
          </button>
        </div>
      </div>

      <!-- Right column -->
      <div class="space-y-2">
        <p class="text-xs font-semibold uppercase tracking-wide text-on-surface-muted">
          {{ lang === 'zh-TW' ? '右側' : 'Right' }}
        </p>
        <div class="space-y-2" role="listbox">
          <button
            v-for="(item, rightIndex) in question.right"
            :key="'right-' + rightIndex"
            type="button"
            role="option"
            :class="rightClasses(rightIndex)"
            @click="onRightTap(rightIndex)"
          >
            <span
              v-if="leftIndexForRight(rightIndex) >= 0"
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-white"
            >
              {{ leftIndexForRight(rightIndex) + 1 }}
            </span>
            <span
              v-else
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 border-border"
            />
            <span class="flex-1 text-on-surface">{{ ltext(item) }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
