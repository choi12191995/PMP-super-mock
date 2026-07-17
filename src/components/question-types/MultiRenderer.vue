<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MultiQ, LText } from '@/core/types'

const props = defineProps<{
  question: MultiQ
  modelValue: number[]
  showFeedback: boolean
  correctAnswer: number[]
  disabled: boolean
  strikeThroughs: Set<number>
  lang: 'en' | 'zh-TW'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
  'update:strikeThroughs': [value: Set<number>]
}>()

const { t } = useI18n()
const longPressTriggered = ref(false)
let pressTimer: ReturnType<typeof setTimeout> | null = null

const atLimit = computed(() => props.modelValue.length >= props.question.selectN)

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function optionLabel(index: number): string {
  return String.fromCharCode(65 + index)
}

function isSelected(index: number): boolean {
  return props.modelValue.includes(index)
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

function onToggle(index: number): void {
  if (longPressTriggered.value) {
    longPressTriggered.value = false
    return
  }
  if (props.disabled || props.strikeThroughs.has(index)) return

  const selected = isSelected(index)
  if (selected) {
    emit(
      'update:modelValue',
      props.modelValue.filter((i) => i !== index),
    )
    return
  }

  if (atLimit.value) return

  emit('update:modelValue', [...props.modelValue, index].sort((a, b) => a - b))
}

function optionClasses(index: number): string[] {
  const selected = isSelected(index)
  const struck = props.strikeThroughs.has(index)
  const isCorrect = props.showFeedback && props.correctAnswer.includes(index)
  const isWrong = props.showFeedback && selected && !props.correctAnswer.includes(index)
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

function checkboxClasses(index: number): string[] {
  const selected = isSelected(index)
  const isCorrect = props.showFeedback && props.correctAnswer.includes(index)
  const isWrong = props.showFeedback && selected && !props.correctAnswer.includes(index)

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
        v-for="(option, index) in question.options"
        :key="index"
        type="button"
        role="checkbox"
        :aria-checked="isSelected(index)"
        :class="optionClasses(index)"
        @pointerdown="onPointerDown(index)"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
        @pointercancel="onPointerUp"
        @click="onToggle(index)"
      >
        <span :class="checkboxClasses(index)">
          <svg
            v-if="isSelected(index)"
            class="h-3.5 w-3.5"
            :class="
              showFeedback && !correctAnswer.includes(index)
                ? 'text-danger'
                : showFeedback && correctAnswer.includes(index)
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
          <span class="mr-2 font-semibold text-on-surface-muted">{{ optionLabel(index) }}.</span>
          {{ ltext(option) }}
        </span>
      </button>
    </div>
  </div>
</template>
