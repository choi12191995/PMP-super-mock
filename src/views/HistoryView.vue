<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db, type AttemptRecord, type AnswerRecord } from '@/db/index'
import type { Band } from '@/core/types'

const router = useRouter()
const { t } = useI18n()

const attempts = ref<AttemptRecord[]>([])
const loading = ref(true)
const confirmClear = ref(false)
const undoRecord = ref<AttemptRecord | null>(null)
const undoAnswers = ref<AnswerRecord[]>([])
const undoTimer = ref<ReturnType<typeof setTimeout> | null>(null)
const showUndo = ref(false)

const swipeState = ref<{ id: string; startX: number; offset: number } | null>(null)
const longPressId = ref<string | null>(null)
let longPressTimer: ReturnType<typeof setTimeout> | null = null

onMounted(loadAttempts)

async function loadAttempts(): Promise<void> {
  loading.value = true
  try {
    attempts.value = await db.attempts
      .where('status')
      .anyOf(['completed', 'quit'])
      .reverse()
      .sortBy('startedAt')
    attempts.value.reverse()
  } finally {
    loading.value = false
  }
}

function modeIcon(mode: string): string {
  const map: Record<string, string> = {
    real: '🎯',
    'full-untimed': '📋',
    free: '♾️',
    custom: '⚙️',
  }
  return map[mode] ?? '📝'
}

function formatDate(ts: number): string {
  return new Date(ts).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDuration(sec: number): string {
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

function bandClasses(band: Band | null): string {
  if (!band) return 'bg-border text-on-surface-muted'
  const map: Record<Band, string> = {
    AT: 'bg-success/15 text-success',
    T: 'bg-primary/15 text-primary',
    BT: 'bg-warning/15 text-warning',
    NI: 'bg-danger/15 text-danger',
  }
  return map[band]
}

function goToResults(id: string): void {
  if (swipeState.value && Math.abs(swipeState.value.offset) > 40) return
  router.push(`/results/${id}`)
}

function onTouchStart(id: string, e: TouchEvent): void {
  swipeState.value = { id, startX: e.touches[0].clientX, offset: 0 }
}

function onTouchMove(e: TouchEvent): void {
  if (!swipeState.value) return
  const dx = e.touches[0].clientX - swipeState.value.startX
  swipeState.value.offset = Math.min(0, dx)
}

async function onTouchEnd(id: string): Promise<void> {
  if (!swipeState.value) return
  if (swipeState.value.offset < -80) {
    await deleteAttempt(id)
  }
  swipeState.value = null
}

function onPointerDown(id: string): void {
  longPressTimer = setTimeout(() => {
    longPressId.value = id
  }, 600)
}

function onPointerUp(): void {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

async function deleteAttempt(id: string): Promise<void> {
  const record = attempts.value.find((a) => a.id === id)
  if (!record) return

  const ans = await db.answers.where('attemptId').equals(id).toArray()
  await db.answers.where('attemptId').equals(id).delete()
  await db.attempts.delete(id)
  attempts.value = attempts.value.filter((a) => a.id !== id)

  undoRecord.value = record
  undoAnswers.value = ans
  showUndo.value = true
  longPressId.value = null

  if (undoTimer.value) clearTimeout(undoTimer.value)
  undoTimer.value = setTimeout(() => {
    showUndo.value = false
    undoRecord.value = null
    undoAnswers.value = []
  }, 5000)
}

async function undoDelete(): Promise<void> {
  if (!undoRecord.value) return
  const record = undoRecord.value
  const ans = undoAnswers.value
  await db.attempts.put(record)
  if (ans.length > 0) await db.answers.bulkPut(ans)
  attempts.value = [...attempts.value, record].sort(
    (a, b) => (b.startedAt ?? 0) - (a.startedAt ?? 0),
  )
  showUndo.value = false
  undoRecord.value = null
  undoAnswers.value = []
  if (undoTimer.value) clearTimeout(undoTimer.value)
}

function requestClearAll(): void {
  confirmClear.value = true
}

async function clearAll(): Promise<void> {
  const all = await db.attempts.toArray()
  for (const att of all) {
    await db.answers.where('attemptId').equals(att.id).delete()
  }
  await db.attempts.clear()
  attempts.value = []
  confirmClear.value = false
}

function cancelClear(): void {
  confirmClear.value = false
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-on-surface">{{ t('history.title') }}</h1>
      <button
        v-if="attempts.length > 0"
        type="button"
        class="rounded-lg px-3 py-1.5 text-sm font-medium text-danger transition hover:bg-danger/10"
        @click="requestClearAll"
      >
        {{ t('history.clearAll') }}
      </button>
    </div>

    <p v-if="loading" class="text-on-surface-muted">{{ t('common.loading') }}</p>

    <div
      v-else-if="attempts.length === 0"
      class="rounded-2xl border border-dashed border-border bg-surface-alt p-12 text-center"
    >
      <p class="text-4xl">📋</p>
      <p class="mt-4 text-on-surface-muted">{{ t('history.empty') }}</p>
      <router-link
        to="/mode"
        class="mt-6 inline-block rounded-xl bg-primary px-6 py-3 font-semibold text-white"
      >
        {{ t('home.startPractice') }}
      </router-link>
    </div>

    <ul v-else class="space-y-3">
      <li
        v-for="att in attempts"
        :key="att.id"
        class="relative overflow-hidden rounded-xl border border-border bg-surface-raised"
      >
        <!-- Delete background -->
        <div
          class="absolute inset-y-0 right-0 flex w-20 items-center justify-center bg-danger text-white"
        >
          {{ t('common.delete') }}
        </div>

        <button
          type="button"
          class="relative flex w-full items-center gap-4 px-4 py-4 text-left transition active:bg-surface-alt"
          :style="
            swipeState?.id === att.id
              ? { transform: `translateX(${swipeState.offset}px)` }
              : undefined
          "
          @click="goToResults(att.id)"
          @touchstart.passive="onTouchStart(att.id, $event)"
          @touchmove.passive="onTouchMove"
          @touchend="onTouchEnd(att.id)"
          @pointerdown="onPointerDown(att.id)"
          @pointerup="onPointerUp"
          @pointerleave="onPointerUp"
        >
          <span class="text-2xl">{{ modeIcon(att.mode) }}</span>
          <div class="min-w-0 flex-1">
            <p class="font-medium text-on-surface">{{ formatDate(att.finishedAt ?? att.startedAt) }}</p>
            <p class="text-sm text-on-surface-muted">
              {{ att.mode }} · {{ formatDuration(att.durationSec) }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-lg font-bold text-on-surface">
              {{ att.score ? Math.round(att.score.pct) : '—' }}%
            </p>
            <span
              v-if="att.band"
              class="inline-block rounded-full px-2 py-0.5 text-xs font-bold"
              :class="bandClasses(att.band)"
            >
              {{ att.band }}
            </span>
          </div>
        </button>

        <!-- Long-press delete -->
        <button
          v-if="longPressId === att.id"
          type="button"
          class="absolute bottom-2 right-2 rounded-lg bg-danger px-3 py-1 text-xs font-semibold text-white"
          @click.stop="deleteAttempt(att.id)"
        >
          {{ t('common.delete') }}
        </button>
      </li>
    </ul>

    <!-- Clear confirmation -->
    <div
      v-if="confirmClear"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    >
      <div class="w-full max-w-sm rounded-2xl bg-surface-raised p-6 shadow-xl">
        <p class="text-on-surface">{{ t('history.clearConfirm') }}</p>
        <div class="mt-4 flex gap-3">
          <button
            type="button"
            class="flex-1 rounded-xl border border-border px-4 py-2 text-on-surface"
            @click="cancelClear"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            type="button"
            class="flex-1 rounded-xl bg-danger px-4 py-2 font-semibold text-white"
            @click="clearAll"
          >
            {{ t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Undo toast -->
    <div
      v-if="showUndo"
      class="fixed bottom-24 left-1/2 z-50 flex -translate-x-1/2 items-center gap-4 rounded-xl bg-on-surface px-5 py-3 text-surface shadow-lg"
    >
      <span class="text-sm">{{ t('history.deleted') }}</span>
      <button
        type="button"
        class="text-sm font-semibold text-primary-light"
        @click="undoDelete"
      >
        {{ t('history.undo') }}
      </button>
    </div>
  </div>
</template>
