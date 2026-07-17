<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MultiQ, LText } from '@/core/types'
import {
  displayToOriginalIndex,
  optionDisplayOrder,
  originalToDisplayIndex,
  remapCorrectListToDisplay,
} from '@/core/shuffleOptions'

const props = defineProps<{
  question: MultiQ
  modelValue: number[]
  showFeedback: boolean
  correctAnswer: number[]
  disabled: boolean
  strikeThroughs: Set<number>
  lang: 'en' | 'zh-TW'
  sessionSeed?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
  'update:strikeThroughs': [value: Set<number>]
}>()

const { t } = useI18n()
const longPressTriggered = ref(false)
let pressTimer: ReturnType<typeof setTimeout> | null = null

const displayOrder = computed(() =>
  optionDisplayOrder(props.question.id, props.question.options.length, props.sessionSeed ?? 0),
)

const shuffledOptions = computed(() =>
  displayOrder.value.map((originalIndex) => props.question.options[originalIndex]),
)

const displayCorrectAnswer = computed(() =>
  remapCorrectListToDisplay(props.correctAnswer, displayOrder.value),
)

const displayModelValue = computed(() =>
  props.modelValue
    .map((originalIndex) => originalToDisplayIndex(originalIndex, displayOrder.value))
    .filter((displayIndex) => displayIndex >= 0)
    .sort((a, b) => a - b),
)

const displayStrikeThroughs = computed(() => {
  const next = new Set<number>()
  for (const originalIndex of props.strikeThroughs) {
    const displayIndex = originalToDisplayIndex(originalIndex, displayOrder.value)
    if (displayIndex >= 0) next.add(displayIndex)
  }
  return next
})

const atLimit = computed(() => displayModelValue.value.length >= props.question.selectN)

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
}

function isSelected(displayIndex: number): boolean {
  return displayModelValue.value.includes(displayIndex)
}

function toggleStrike(displayIndex: number): void {
  const originalIndex = displayToOriginalIndex(displayIndex, displayOrder.value)
  const next = new Set(props.strikeThroughs)
  if (next.has(originalIndex)) next.delete(originalIndex)
  else next.add(originalIndex)
  emit('update:strikeThroughs', next)
}

function onPointerDown(displayIndex: number): void {
  longPressTriggered.value = false
  if (pressTimer) clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    longPressTriggered.value = true
    toggleStrike(displayIndex)
    if (navigator.vibrate) navigator.vibrate(10)
  }, 500)
}

function onPointerUp(): void {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
}

function onToggle(displayIndex: number): void {
  if (longPressTriggered.value) {
    longPressTriggered.value = false
    return
  }
  if (props.disabled || displayStrikeThroughs.value.has(displayIndex)) return

  const originalIndex = displayToOriginalIndex(displayIndex, displayOrder.value)
  const selected = isSelected(displayIndex)
  if (selected) {
    emit(
      'update:modelValue',
      props.modelValue.filter((i) => i !== originalIndex),
    )
    return
  }

  if (atLimit.value) return

  emit('update:modelValue', [...props.modelValue, originalIndex].sort((a, b) => a - b))
}

function optionClasses(displayIndex: number): string[] {
  const selected = isSelected(displayIndex)
  const struck = displayStrikeThroughs.value.has(displayIndex)
  const isCorrect = props.showFeedback && displayCorrectAnswer.value.includes(displayIndex)
  const isWrong = props.showFeedback && selected && !displayCorrectAnswer.value.includes(displayIndex)
  const blocked = !selected && atLimit.value && !props.showFeedback

  const classes = [
    'group flex min-h-[44px] w-full cursor-pointer items-start gap-3 rounded-xl border-2 px-4 py-3 text-left transition',
    'touch-manipulation select-none active:scale-[0.99]',
  ]

  if (struck) {
    classes.push('border-border opacity-50 line-through')
  } else if (isCorrect) {
    classes.push('border-success bg-success/10')
  } else if (isWrong) {
    classes.push('border-danger bg-danger/10')
  } else if (selected) {
    classes.push('border-primary bg-primary/5')
  } else if (blocked) {
    classes.push('cursor-not-allowed border-border bg-surface-alt opacity-60')
  } else {
    classes.push('border-border bg-surface-raised hover:border-primary/50')
  }

  if (props.disabled && !props.showFeedback) {
    classes.push('pointer-events-none opacity-70')
  }

  return classes
}

function checkboxClasses(displayIndex: number): string[] {
  const selected = isSelected(displayIndex)
  const isCorrect = props.showFeedback && displayCorrectAnswer.value.includes(displayIndex)
  const isWrong = props.showFeedback && selected && !displayCorrectAnswer.value.includes(displayIndex)

  const classes = [
    'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border-2 transition',
  ]

  if (isCorrect) classes.push('border-success bg-success/20')
  else if (isWrong) classes.push('border-danger bg-danger/20')
  else if (selected) classes.push('border-primary bg-primary/10')
  else classes.push('border-border group-hover:border-primary/50')

  return classes
}
</script>

<template>
  <div class="space-y-5">
    <p
      class="inline-flex rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary"
    >
      {{ t('exam.selectN', { n: question.selectN }) }}
    </p>

    <p class="text-base leading-relaxed text-on-surface whitespace-pre-wrap">
      {{ ltext(question.stem) }}
    </p>

    <div class="space-y-3" role="group" :aria-label="ltext(question.stem)">
      <button
        v-for="(option, displayIndex) in shuffledOptions"
        :key="displayOrder[displayIndex]"
        type="button"
        role="checkbox"
        :aria-checked="isSelected(displayIndex)"
        :class="optionClasses(displayIndex)"
        @pointerdown="onPointerDown(displayIndex)"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
        @pointercancel="onPointerUp"
        @click="onToggle(displayIndex)"
      >
        <span :class="checkboxClasses(displayIndex)">
          <svg
            v-if="isSelected(displayIndex)"
            class="h-3.5 w-3.5"
            :class="
              showFeedback && !displayCorrectAnswer.includes(displayIndex)
                ? 'text-danger'
                : showFeedback && displayCorrectAnswer.includes(displayIndex)
                  ? 'text-success'
                  : 'text-primary'
            "
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </span>
        <span class="flex-1 text-sm leading-relaxed text-on-surface sm:text-base">
          <span class="mr-2 font-semibold text-on-surface-muted">{{ optionLabel(displayIndex) }}.</span>
          {{ ltext(option) }}
        </span>
      </button>
    </div>
  </div>
</template>
