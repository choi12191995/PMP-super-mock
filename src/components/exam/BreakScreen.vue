<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  breakDuration: number
  breakNumber: 1 | 2
}>()

const emit = defineEmits<{
  resume: []
  skip: []
}>()

const { t } = useI18n()
const remaining = ref(props.breakDuration)
let interval: ReturnType<typeof setInterval> | null = null

const timerLabel = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

onMounted(() => {
  interval = setInterval(() => {
    if (remaining.value > 0) {
      remaining.value -= 1
    } else {
      emit('resume')
    }
  }, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>

<template>
  <div class="mx-auto flex min-h-[calc(100vh-8rem)] max-w-lg flex-col items-center justify-center px-4 py-12">
    <div class="w-full rounded-2xl border border-border bg-surface-raised p-8 text-center shadow-sm">
      <h1 class="mb-2 text-2xl font-bold text-on-surface">{{ t('exam.breakTitle') }}</h1>
      <p class="mb-6 text-sm text-on-surface-muted">{{ t('exam.breakMessage') }}</p>

      <div class="mb-8 font-mono text-5xl font-bold tabular-nums text-primary">
        {{ timerLabel }}
      </div>

      <div class="flex flex-col gap-3 sm:flex-row sm:justify-center">
        <button
          type="button"
          class="min-h-[48px] rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-primary-dark"
          @click="emit('resume')"
        >
          {{ t('exam.resumeExam') }}
        </button>
        <button
          type="button"
          class="min-h-[48px] rounded-xl border border-border px-6 py-3 text-sm font-semibold text-on-surface transition hover:border-primary"
          @click="emit('skip')"
        >
          {{ t('exam.skipBreak') }}
        </button>
      </div>
    </div>
  </div>
</template>
