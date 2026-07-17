<script setup lang="ts">
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TimerMode } from '@/core/engine/timer'

const props = defineProps<{
  timeRemaining: number
  timeElapsed: number
  timerMode: TimerMode
  questionIndex: number
  totalQuestions: number
  sectionLabel: string
  isFlagged: boolean
  timerVisible: boolean
}>()

const emit = defineEmits<{
  'toggle-flag': []
  'toggle-timer-visible': []
  'time-warning': [minutes: number]
}>()

const { t } = useI18n()

const warningsEmitted = new Set<number>()

const displaySeconds = computed(() => {
  if (props.timerMode === 'countdown') return props.timeRemaining
  if (props.timerMode === 'count-up') return props.timeElapsed
  return 0
})

const timerLabel = computed(() => {
  const total = Math.max(0, Math.floor(displaySeconds.value))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${m}:${String(s).padStart(2, '0')}`
})

const timerColorClass = computed(() => {
  if (props.timerMode !== 'countdown') return 'text-on-surface'
  const mins = props.timeRemaining / 60
  if (mins <= 5) return 'text-danger'
  if (mins <= 30) return 'text-warning'
  return 'text-on-surface'
})

function checkWarnings(): void {
  if (props.timerMode !== 'countdown') return
  const mins = Math.floor(props.timeRemaining / 60)
  for (const threshold of [60, 30, 10, 5]) {
    if (mins === threshold && !warningsEmitted.has(threshold)) {
      warningsEmitted.add(threshold)
      emit('time-warning', threshold)
    }
  }
}

defineExpose({ checkWarnings })

watch(() => props.timeRemaining, checkWarnings, { immediate: true })
</script>

<template>
  <div
    class="glass-card mb-4 flex items-center justify-between gap-3 px-4 py-3"
  >
    <div class="min-w-0 flex-1">
      <p v-if="sectionLabel" class="text-xs font-medium uppercase tracking-wide text-on-surface-muted">
        {{ sectionLabel }}
      </p>
      <p class="text-lg font-bold text-on-surface">
        {{ t('exam.question') }} {{ questionIndex + 1 }}
        <span class="font-normal text-on-surface-muted">{{ t('exam.of') }}</span>
        {{ totalQuestions }}
      </p>
    </div>

    <button
      v-if="timerMode !== 'off'"
      type="button"
      class="min-h-[44px] rounded-xl border border-border px-4 py-2 font-mono text-lg font-semibold tabular-nums transition hover:border-primary"
      :class="timerColorClass"
      @click="emit('toggle-timer-visible')"
    >
      <span v-if="timerVisible">{{ timerLabel }}</span>
      <span v-else class="text-on-surface-muted">--:--</span>
    </button>

    <button
      type="button"
      class="flex min-h-[44px] min-w-[44px] items-center justify-center rounded-xl border border-border px-3 transition hover:border-primary"
      :class="isFlagged ? 'border-warning bg-warning/10 text-warning' : 'text-on-surface-muted'"
      @click="emit('toggle-flag')"
    >
      <span class="text-lg">{{ isFlagged ? '🚩' : '⚑' }}</span>
      <span class="sr-only">{{ isFlagged ? t('exam.unflag') : t('exam.flag') }}</span>
    </button>
  </div>
</template>
