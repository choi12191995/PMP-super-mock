<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db } from '@/db/index'
import { loadAllQuestions, loadManifest } from '@/core/bank/loader'
import { EXAM } from '@/core/examConstants'
import {
  computeOverview,
  computeScoreTrend,
  computeDomainRadar,
  computeTaskHeatmap,
  computeReadiness,
  findBestAttempt,
  findLatestAttempt,
  buildDailyFromAnswers,
} from '@/core/stats'
import { useSettingsStore } from '@/stores/settings'
import ScoreTrendChart from '@/components/charts/ScoreTrendChart.vue'
import DomainRadarChart from '@/components/charts/DomainRadarChart.vue'
import TaskHeatmap from '@/components/charts/TaskHeatmap.vue'
import StreakCalendar from '@/components/charts/StreakCalendar.vue'

const router = useRouter()
const { t } = useI18n()
const settings = useSettingsStore()

const loading = ref(true)
const overview = ref<ReturnType<typeof computeOverview> | null>(null)
const scoreTrend = ref<ReturnType<typeof computeScoreTrend>>([])
const domainRadar = ref<ReturnType<typeof computeDomainRadar>>([])
const taskHeatmap = ref<ReturnType<typeof computeTaskHeatmap>>([])
const dailyData = ref<{ date: string; answered: number }[]>([])
const readiness = ref<{ label: string; hint: string }>({ label: 'keepGoing', hint: '' })

const daysUntilExam = computed(() => {
  if (!settings.examDate) return null
  const diff = new Date(settings.examDate).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / 86400000))
})

const readinessLabel = computed(() => {
  if (readiness.value.label === 'onTrack') return t('dashboard.onTrack')
  if (readiness.value.label === 'pushDomain') {
    const domainMap: Record<string, string> = {
      people: t('common.people'),
      process: t('common.process'),
      business: t('common.business'),
    }
    return t('dashboard.pushDomain', {
      domain: domainMap[readiness.value.hint] ?? readiness.value.hint,
    })
  }
  return t('dashboard.keepGoing')
})

onMounted(async () => {
  try {
    const [attempts, answers, daily, manifest, questions] = await Promise.all([
      db.attempts.where('status').anyOf(['completed', 'quit']).toArray(),
      db.answers.toArray(),
      db.daily.toArray(),
      loadManifest(),
      loadAllQuestions(),
    ])

    const taskByQuestionId: Record<string, string> = {}
    for (const q of questions) {
      taskByQuestionId[q.id] = q.task
    }

    const ov = computeOverview(attempts, daily, manifest.counts.total, answers)
    overview.value = ov
    scoreTrend.value = computeScoreTrend(attempts)

    const latest = findLatestAttempt(attempts)
    const best = findBestAttempt(attempts)
    domainRadar.value = computeDomainRadar(latest, best)
    taskHeatmap.value = computeTaskHeatmap(answers, taskByQuestionId)

    const dailyRecords =
      daily.length > 0 ? daily : buildDailyFromAnswers(answers)
    dailyData.value = dailyRecords.map((d) => ({
      date: d.date,
      answered: d.answered,
    }))

    const domainScores: Record<string, number> = {}
    if (latest?.score?.byDomain) {
      for (const [domain, stats] of Object.entries(latest.score.byDomain)) {
        domainScores[domain] =
          stats.total === 0 ? 0 : (stats.correct / stats.total) * 100
      }
    }
    readiness.value = computeReadiness(ov, domainScores)
  } finally {
    loading.value = false
  }
})

function onTaskSelect(task: string): void {
  router.push({ path: '/mode', query: { mode: 'custom', tasks: task } })
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-6 text-2xl font-bold text-on-surface">{{ t('dashboard.title') }}</h1>

    <p v-if="loading" class="text-on-surface-muted">{{ t('common.loading') }}</p>

    <template v-else-if="overview">
      <!-- Exam countdown -->
      <div
        v-if="daysUntilExam !== null"
        class="mb-6 rounded-2xl bg-primary p-6 text-center text-white"
      >
        <p class="text-3xl font-bold">{{ t('home.examCountdown', { days: daysUntilExam }) }}</p>
      </div>
      <div v-else class="mb-6 rounded-2xl border border-border bg-surface-alt p-4 text-center">
        <p class="text-sm text-on-surface-muted">{{ t('home.noExamDate') }}</p>
      </div>

      <!-- Readiness -->
      <div class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-on-surface-muted">
          {{ t('dashboard.readiness') }}
        </p>
        <p class="mt-1 text-xl font-bold text-on-surface">{{ readinessLabel }}</p>
      </div>

      <!-- Score trend -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('dashboard.scoreTrend') }}</h2>
        <ScoreTrendChart :data="scoreTrend" :pass-line="EXAM.PASS_PROXY_PCT" />
      </section>

      <!-- Domain radar -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('dashboard.domainRadar') }}</h2>
        <DomainRadarChart :data="domainRadar" />
      </section>

      <!-- Task heatmap -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('dashboard.taskHeatmap') }}</h2>
        <TaskHeatmap :data="taskHeatmap" @select="onTaskSelect" />
        <div class="mt-3 flex flex-wrap gap-3 text-xs text-on-surface-muted">
          <span class="flex items-center gap-1"><span class="inline-block h-3 w-3 rounded bg-success/80" /> {{ t('dashboard.legendHigh') }}</span>
          <span class="flex items-center gap-1"><span class="inline-block h-3 w-3 rounded bg-warning/70" /> {{ t('dashboard.legendMid') }}</span>
          <span class="flex items-center gap-1"><span class="inline-block h-3 w-3 rounded bg-danger/70" /> {{ t('dashboard.legendLow') }}</span>
          <span class="flex items-center gap-1"><span class="inline-block h-3 w-3 rounded bg-border/40" /> {{ t('dashboard.legendUnseen') }}</span>
        </div>
      </section>

      <!-- Streak calendar -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-on-surface">{{ t('dashboard.streakCalendar') }}</h2>
          <div class="flex gap-4 text-sm">
            <div>
              <p class="text-on-surface-muted">{{ t('dashboard.currentStreak') }}</p>
              <p class="text-xl font-bold text-on-surface">{{ overview.currentStreak }}</p>
            </div>
            <div>
              <p class="text-on-surface-muted">{{ t('dashboard.bestStreak') }}</p>
              <p class="text-xl font-bold text-on-surface">{{ overview.bestStreak }}</p>
            </div>
          </div>
        </div>
        <StreakCalendar :daily-data="dailyData" />
      </section>

      <!-- Coverage -->
      <section class="rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('dashboard.coverage') }}</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-on-surface-muted">{{ t('dashboard.seen') }}</p>
            <p class="text-2xl font-bold text-on-surface">{{ Math.round(overview.coveragePct) }}%</p>
          </div>
          <div>
            <p class="text-sm text-on-surface-muted">{{ t('dashboard.mastered') }}</p>
            <p class="text-2xl font-bold text-on-surface">{{ Math.round(overview.masteredPct) }}%</p>
          </div>
        </div>
        <p class="mt-2 text-xs text-on-surface-muted">
          {{ overview.totalAnswered }} {{ t('home.questionsAnswered').toLowerCase() }}
          · {{ overview.totalAttempts }} attempts
        </p>
      </section>
    </template>
  </div>
</template>
