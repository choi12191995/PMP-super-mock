<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '@/stores/settings'
import { computed } from 'vue'
import { db } from '@/db/index'
import { loadManifest } from '@/core/bank/loader'
import { computeOverview, findLatestAttempt } from '@/core/stats'

const { t } = useI18n()
const settings = useSettingsStore()

const recentScore = ref<number | null>(null)
const totalAnswered = ref(0)
const currentStreak = ref(0)
const coveragePct = ref(0)
const loading = ref(true)

const daysUntilExam = computed(() => {
  if (!settings.examDate) return null
  const diff = new Date(settings.examDate).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / 86400000))
})

onMounted(async () => {
  try {
    const [attempts, answers, daily, manifest] = await Promise.all([
      db.attempts.where('status').anyOf(['completed', 'quit']).toArray(),
      db.answers.toArray(),
      db.daily.toArray(),
      loadManifest(),
    ])

    const overview = computeOverview(attempts, daily, manifest.counts.total, answers)
    totalAnswered.value = overview.totalAnswered
    currentStreak.value = overview.currentStreak
    coveragePct.value = overview.coveragePct

    const latest = findLatestAttempt(attempts)
    recentScore.value = latest?.score ? Math.round(latest.score.pct) : null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <section class="mb-8 text-center">
      <h1 class="mb-2 text-2xl font-bold text-on-surface">{{ t('home.welcome') }}</h1>
      <p class="text-sm text-on-surface-muted">{{ t('app.tagline') }}</p>
    </section>

    <div
      v-if="daysUntilExam !== null"
      class="mb-6 rounded-2xl bg-primary p-6 text-center text-white"
    >
      <p class="text-3xl font-bold">{{ t('home.examCountdown', { days: daysUntilExam }) }}</p>
    </div>
    <div v-else class="mb-6 rounded-2xl border border-border bg-surface-alt p-6 text-center">
      <p class="text-on-surface-muted">{{ t('home.noExamDate') }}</p>
    </div>

    <router-link
      to="/mode"
      class="mb-8 flex w-full items-center justify-center rounded-2xl bg-primary px-8 py-4 text-lg font-semibold text-white shadow-md transition hover:bg-primary-dark active:scale-[0.98]"
    >
      {{ t('home.startPractice') }}
    </router-link>

    <div class="grid grid-cols-2 gap-4">
      <div class="rounded-xl border border-border bg-surface-raised p-4">
        <p class="text-xs text-on-surface-muted">{{ t('home.recentScore') }}</p>
        <p class="mt-1 text-2xl font-bold text-on-surface">
          {{ loading ? '…' : recentScore !== null ? `${recentScore}%` : '—' }}
        </p>
      </div>
      <div class="rounded-xl border border-border bg-surface-raised p-4">
        <p class="text-xs text-on-surface-muted">{{ t('home.questionsAnswered') }}</p>
        <p class="mt-1 text-2xl font-bold text-on-surface">
          {{ loading ? '…' : totalAnswered }}
        </p>
      </div>
      <div class="rounded-xl border border-border bg-surface-raised p-4">
        <p class="text-xs text-on-surface-muted">{{ t('home.streak') }}</p>
        <p class="mt-1 text-2xl font-bold text-on-surface">
          {{ loading ? '…' : currentStreak }}
        </p>
      </div>
      <div class="rounded-xl border border-border bg-surface-raised p-4">
        <p class="text-xs text-on-surface-muted">{{ t('home.coverage') }}</p>
        <p class="mt-1 text-2xl font-bold text-on-surface">
          {{ loading ? '…' : `${Math.round(coveragePct)}%` }}
        </p>
      </div>
    </div>
  </div>
</template>
