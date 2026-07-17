<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()

const display = ref('0')
const storedValue = ref<number | null>(null)
const pendingOp = ref<string | null>(null)
const freshEntry = ref(true)

function formatDisplay(value: number): string {
  if (!Number.isFinite(value)) return t('exam.calculatorError')
  const str = String(value)
  if (str.length > 12) return value.toExponential(6)
  return str
}

function inputDigit(digit: string): void {
  if (freshEntry.value) {
    display.value = digit
    freshEntry.value = false
  } else {
    display.value = display.value === '0' ? digit : display.value + digit
  }
}

function inputDecimal(): void {
  if (freshEntry.value) {
    display.value = '0.'
    freshEntry.value = false
    return
  }
  if (!display.value.includes('.')) {
    display.value += '.'
  }
}

function clearAll(): void {
  display.value = '0'
  storedValue.value = null
  pendingOp.value = null
  freshEntry.value = true
}

function backspace(): void {
  if (freshEntry.value) return
  if (display.value.length <= 1 || (display.value.length === 2 && display.value.startsWith('-'))) {
    display.value = '0'
    freshEntry.value = true
    return
  }
  display.value = display.value.slice(0, -1)
}

function applyUnary(fn: (n: number) => number): void {
  const current = parseFloat(display.value)
  display.value = formatDisplay(fn(current))
  freshEntry.value = true
}

function percent(): void {
  const current = parseFloat(display.value)
  if (storedValue.value !== null && pendingOp.value) {
    display.value = formatDisplay((storedValue.value * current) / 100)
  } else {
    display.value = formatDisplay(current / 100)
  }
  freshEntry.value = true
}

function sqrt(): void {
  applyUnary((n) => Math.sqrt(n))
}

function setOperator(op: string): void {
  const current = parseFloat(display.value)
  if (storedValue.value !== null && pendingOp.value && !freshEntry.value) {
    compute()
  } else {
    storedValue.value = current
  }
  pendingOp.value = op
  freshEntry.value = true
}

function compute(): void {
  if (storedValue.value === null || !pendingOp.value) return
  const current = parseFloat(display.value)
  let result = current
  switch (pendingOp.value) {
    case '+':
      result = storedValue.value + current
      break
    case '-':
      result = storedValue.value - current
      break
    case '×':
      result = storedValue.value * current
      break
    case '÷':
      result = current === 0 ? NaN : storedValue.value / current
      break
  }
  display.value = formatDisplay(result)
  storedValue.value = null
  pendingOp.value = null
  freshEntry.value = true
}

type CalcButton = {
  label: string
  action: () => void
  variant?: 'action' | 'operator' | 'equals'
  ariaLabel?: string
}

const buttons: CalcButton[] = [
  { label: 'C', action: clearAll, variant: 'action', ariaLabel: 'exam.calculatorClear' },
  { label: '⌫', action: backspace, variant: 'action', ariaLabel: 'exam.calculatorBackspace' },
  { label: '%', action: percent, variant: 'operator' },
  { label: '√', action: sqrt, variant: 'operator', ariaLabel: 'exam.calculatorSqrt' },
  { label: '7', action: () => inputDigit('7') },
  { label: '8', action: () => inputDigit('8') },
  { label: '9', action: () => inputDigit('9') },
  { label: '÷', action: () => setOperator('÷'), variant: 'operator' },
  { label: '4', action: () => inputDigit('4') },
  { label: '5', action: () => inputDigit('5') },
  { label: '6', action: () => inputDigit('6') },
  { label: '×', action: () => setOperator('×'), variant: 'operator' },
  { label: '1', action: () => inputDigit('1') },
  { label: '2', action: () => inputDigit('2') },
  { label: '3', action: () => inputDigit('3') },
  { label: '-', action: () => setOperator('-'), variant: 'operator' },
  { label: '0', action: () => inputDigit('0') },
  { label: '.', action: inputDecimal },
  { label: '=', action: compute, variant: 'equals' },
  { label: '+', action: () => setOperator('+'), variant: 'operator' },
]

function buttonClass(variant?: string): string {
  const base =
    'touch-target flex min-h-[44px] items-center justify-center rounded-xl text-lg font-semibold transition active:scale-95 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
  switch (variant) {
    case 'action':
      return `${base} bg-surface-alt text-danger hover:bg-danger/10`
    case 'operator':
      return `${base} bg-primary/10 text-primary hover:bg-primary/20`
    case 'equals':
      return `${base} bg-primary text-white hover:bg-primary-dark`
    default:
      return `${base} border border-border bg-surface-raised text-on-surface hover:border-primary/50`
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
      role="dialog"
      :aria-label="t('exam.calculator')"
      aria-modal="true"
    >
      <button
        type="button"
        class="absolute inset-0 bg-black/50"
        :aria-label="t('common.close')"
        @click="emit('close')"
      />

      <div
        class="glass-modal relative w-full max-w-sm p-4 sm:rounded-[var(--glass-radius-lg)]" style="border-radius: var(--glass-radius-lg) var(--glass-radius-lg) 0 0"
      >
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-bold text-on-surface">{{ t('exam.calculator') }}</h2>
          <button
            type="button"
            class="touch-target rounded-xl px-3 py-2 text-sm font-medium text-on-surface-muted hover:bg-surface-alt"
            @click="emit('close')"
          >
            {{ t('common.close') }}
          </button>
        </div>

        <div
          class="mb-4 overflow-hidden rounded-xl border border-border bg-surface px-4 py-3 text-right font-mono text-3xl font-bold tabular-nums text-on-surface"
          aria-live="polite"
          aria-atomic="true"
        >
          {{ display }}
        </div>

        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="(btn, index) in buttons"
            :key="index"
            type="button"
            :class="buttonClass(btn.variant)"
            :aria-label="btn.ariaLabel ? t(btn.ariaLabel) : btn.label"
            @click="btn.action"
          >
            {{ btn.label }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
