<script setup lang="ts">
import { ref } from 'vue'
import type { McqQ, LText } from '@/core/types'

const props = defineProps<{
  question: McqQ
  modelValue: number | null
  showFeedback: boolean
  correctAnswer: number
  disabled: boolean
  strikeThroughs: Set<number>
  lang: 'en' | 'zh-TW'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'update:strikeThroughs': [value: Set<number>]
}>()

const longPressTriggered = ref(false)
let pressTimer: ReturnType<typeof setTimeout> | null = null

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
}

function toggleStrike(index: number): void {
  const next = new Set(props.strikeThroughs)
  if (next.has(index)) next.delete(index)
  else next.add(index)
  emit('update:strikeThroughs', next)
}

function onPointerDown(index: number): void {
  longPressTriggered.value = false
  if (pressTimer) clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    longPressTriggered.value = true
    toggleStrike(index)
    if (navigator.vibrate) navigator.vibrate(10)
  }, 500)
}

function onPointerUp(): void {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
}

function onSelect(index: number): void {
  if (longPressTriggered.value) {
    longPressTriggered.value = false
    return
  }
  if (props.disabled || props.strikeThroughs.has(index)) return
  emit('update:modelValue', index)
}

function optionClasses(index: number): string[] {
  const selected = props.modelValue === index
  const struck = props.strikeThroughs.has(index)
  const isCorrect = props.showFeedback && index === props.correctAnswer
  const isWrong = props.showFeedback && selected && index !== props.correctAnswer

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

function radioClasses(index: number): string[] {
  const selected = props.modelValue === index
  const isCorrect = props.showFeedback && index === props.correctAnswer
  const isWrong = props.showFeedback && selected && index !== props.correctAnswer

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
        v-for="(option, index) in question.options"
        :key="index"
        type="button"
        role="radio"
        :aria-checked="modelValue === index"
        :class="optionClasses(index)"
        @pointerdown="onPointerDown(index)"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
        @pointercancel="onPointerUp"
        @click="onSelect(index)"
      >
        <span :class="radioClasses(index)">
          <span
            v-if="modelValue === index"
            class="h-2.5 w-2.5 rounded-full"
            :class="
              showFeedback && index !== correctAnswer
                ? 'bg-danger'
                : showFeedback && index === correctAnswer
                  ? 'bg-success'
                  : 'bg-primary'
            "
          />
        </span>
        <span class="flex-1 text-sm leading-relaxed text-on-surface sm:text-base">
          <span class="mr-2 font-semibold text-on-surface-muted">{{ optionLabel(index) }}.</span>
          {{ ltext(option) }}
        </span>
      </button>
    </div>
  </div>
</template>
