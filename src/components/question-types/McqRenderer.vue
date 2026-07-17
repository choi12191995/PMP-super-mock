<script setup lang="ts">
import { computed, ref } from 'vue'
import type { McqQ, LText } from '@/core/types'
import {
  displayToOriginalIndex,
  optionDisplayOrder,
  originalToDisplayIndex,
  remapCorrectToDisplay,
} from '@/core/shuffleOptions'

const props = defineProps<{
  question: McqQ
  modelValue: number | null
  showFeedback: boolean
  correctAnswer: number
  disabled: boolean
  strikeThroughs: Set<number>
  lang: 'en' | 'zh-TW'
  sessionSeed?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'update:strikeThroughs': [value: Set<number>]
}>()

const longPressTriggered = ref(false)
let pressTimer: ReturnType<typeof setTimeout> | null = null

const displayOrder = computed(() =>
  optionDisplayOrder(props.question.id, props.question.options.length, props.sessionSeed ?? 0),
)

const shuffledOptions = computed(() =>
  displayOrder.value.map((originalIndex) => props.question.options[originalIndex]),
)

const displayCorrectAnswer = computed(() =>
  remapCorrectToDisplay(props.correctAnswer, displayOrder.value),
)

const displayModelValue = computed(() => {
  if (props.modelValue === null) return null
  const displayIndex = originalToDisplayIndex(props.modelValue, displayOrder.value)
  return displayIndex >= 0 ? displayIndex : null
})

const displayStrikeThroughs = computed(() => {
  const next = new Set<number>()
  for (const originalIndex of props.strikeThroughs) {
    const displayIndex = originalToDisplayIndex(originalIndex, displayOrder.value)
    if (displayIndex >= 0) next.add(displayIndex)
  }
  return next
})

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
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

function onSelect(displayIndex: number): void {
  if (longPressTriggered.value) {
    longPressTriggered.value = false
    return
  }
  if (props.disabled || displayStrikeThroughs.value.has(displayIndex)) return
  const originalIndex = displayToOriginalIndex(displayIndex, displayOrder.value)
  emit('update:modelValue', originalIndex)
}

function optionClasses(displayIndex: number): string[] {
  const selected = displayModelValue.value === displayIndex
  const struck = displayStrikeThroughs.value.has(displayIndex)
  const isCorrect = props.showFeedback && displayIndex === displayCorrectAnswer.value
  const isWrong =
    props.showFeedback && selected && displayIndex !== displayCorrectAnswer.value

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
  } else {
    classes.push('border-border bg-surface-raised hover:border-primary/50')
  }

  if (props.disabled && !props.showFeedback) {
    classes.push('pointer-events-none opacity-70')
  }

  return classes
}

function radioClasses(displayIndex: number): string[] {
  const selected = displayModelValue.value === displayIndex
  const isCorrect = props.showFeedback && displayIndex === displayCorrectAnswer.value
  const isWrong =
    props.showFeedback && selected && displayIndex !== displayCorrectAnswer.value

  const classes = [
    'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition',
  ]

  if (isCorrect) classes.push('border-success')
  else if (isWrong) classes.push('border-danger')
  else if (selected) classes.push('border-primary')
  else classes.push('border-border group-hover:border-primary/50')

  return classes
}
</script>

<template>
  <div class="space-y-5">
    <p class="text-base leading-relaxed text-on-surface whitespace-pre-wrap">
      {{ ltext(question.stem) }}
    </p>

    <div class="space-y-3" role="radiogroup" :aria-label="ltext(question.stem)">
      <button
        v-for="(option, displayIndex) in shuffledOptions"
        :key="displayOrder[displayIndex]"
        type="button"
        role="radio"
        :aria-checked="displayModelValue === displayIndex"
        :class="optionClasses(displayIndex)"
        @pointerdown="onPointerDown(displayIndex)"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
        @pointercancel="onPointerUp"
        @click="onSelect(displayIndex)"
      >
        <span :class="radioClasses(displayIndex)">
          <span
            v-if="displayModelValue === displayIndex"
            class="h-2.5 w-2.5 rounded-full"
            :class="
              showFeedback && displayIndex !== displayCorrectAnswer
                ? 'bg-danger'
                : showFeedback && displayIndex === displayCorrectAnswer
                  ? 'bg-success'
                  : 'bg-primary'
            "
          />
        </span>
        <span class="flex-1 text-sm leading-relaxed text-on-surface sm:text-base">
          <span class="mr-2 font-semibold text-on-surface-muted">{{ optionLabel(displayIndex) }}.</span>
          {{ ltext(option) }}
        </span>
      </button>
    </div>
  </div>
</template>
