<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db, type AttemptRecord, type AnswerRecord } from '@/db/index'
import { EXAM } from '@/core/examConstants'
import { computeBand, computeDomainBands } from '@/core/engine/scoring'
import { loadAllQuestions } from '@/core/bank/loader'
import { findBestAttempt } from '@/core/stats'
import { playPassSound, hapticPass } from '@/core/feedback'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import WeakPointCard from '@/components/ai/WeakPointCard.vue'
import type { Band, Domain, LText, Question } from '@/core/types'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const attempt = ref<AttemptRecord | null>(null)
const answers = ref<AnswerRecord[]>([])
const questions = ref<Map<string, Question>>(new Map())
const loading = ref(true)
const showConfetti = ref(false)

const attemptId = computed(() => route.params.attemptId as string)

onMounted(async () => {
  try {
    const [att, ans, allQuestions, allAttempts] = await Promise.all([
      db.attempts.get(attemptId.value),
      db.answers.where('attemptId').equals(attemptId.value).toArray(),
      loadAllQuestions(),
      db.attempts.where('status').equals('completed').toArray(),
    ])

    attempt.value = att ?? null
    answers.value = ans
    questions.value = new Map(allQuestions.map((q) => [q.id, q]))

    const best = findBestAttempt(allAttempts)
    const isPersonalBest =
      att?.score != null && best?.id === att.id && allAttempts.length > 1

    if (att?.passedProxy || isPersonalBest) {
      showConfetti.value = true
      if (att?.passedProxy) {
        playPassSound()
        hapticPass()
      }
      setTimeout(() => {
        showConfetti.value = false
      }, 4000)
    }
  } finally {
    loading.value = false
  }
})

function ltext(text: LText): string {
  return locale.value === 'zh-TW' ? text.zh : text.en
}

function formatDuration(sec: number): string {
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

const score = computed(() => attempt.value?.score)
const pct = computed(() => Math.round(score.value?.pct ?? 0))
const passed = computed(() => attempt.value?.passedProxy ?? false)
const isPartial = computed(() => {
  if (!score.value) return false
  return answers.value.length < score.value.max
})

const domainBands = computed(() => {
  if (!score.value) return {} as Record<string, Band>
  return computeDomainBands(score.value.byDomain)
})

function bandLabel(band: Band): string {
  const map: Record<Band, string> = {
    AT: t('results.aboveTarget'),
    T: t('results.target'),
    BT: t('results.belowTarget'),
    NI: t('results.needsImprovement'),
  }
  return map[band]
}

function bandClasses(band: Band): string {
  const map: Record<Band, string> = {
    AT: 'bg-success/15 text-success border-success/40',
    T: 'bg-primary/15 text-primary border-primary/40',
    BT: 'bg-warning/15 text-warning border-warning/40',
    NI: 'bg-danger/15 text-danger border-danger/40',
  }
  return map[band]
}

function domainLabel(domain: string): string {
  const map: Record<string, string> = {
    people: t('common.people'),
    process: t('common.process'),
    business: t('common.business'),
  }
  return map[domain] ?? domain
}

function domainPct(domain: string): number {
  const stats = score.value?.byDomain[domain]
  if (!stats || stats.total === 0) return 0
  return Math.round((stats.correct / stats.total) * 100)
}

const taskChart = computed(() => {
  if (!score.value) return { labels: [], values: [] }
  const entries = Object.entries(score.value.byTask)
    .filter(([, s]) => s.total > 0)
    .sort((a, b) => a[0].localeCompare(b[0]))
  return {
    labels: entries.map(([task]) => task),
    values: entries.map(([, s]) => Math.round((s.correct / s.total) * 100)),
  }
})

const typeChart = computed(() => {
  if (!score.value) return { labels: [], values: [] }
  const entries = Object.entries(score.value.byType).filter(([, s]) => s.total > 0)
  return {
    labels: entries.map(([type]) => type),
    values: entries.map(([, s]) => Math.round((s.correct / s.total) * 100)),
  }
})

const approachChart = computed(() => {
  if (!score.value) return { labels: [], values: [] }
  const entries = Object.entries(score.value.byApproach).filter(([, s]) => s.total > 0)
  const labelMap: Record<string, string> = {
    predictive: t('common.predictive'),
    agile: t('common.agile'),
    hybrid: t('common.hybrid'),
  }
  return {
    labels: entries.map(([a]) => labelMap[a] ?? a),
    values: entries.map(([, s]) => Math.round((s.correct / s.total) * 100)),
  }
})

const avgTimeSec = computed(() => {
  if (answers.value.length === 0) return 0
  const total = answers.value.reduce((s, a) => s + a.timeSec, 0)
  return Math.round(total / answers.value.length)
})

const slowestQuestions = computed(() => {
  return [...answers.value]
    .sort((a, b) => b.timeSec - a.timeSec)
    .slice(0, 10)
    .map((ans) => {
      const q = questions.value.get(ans.questionId)
      const stem = q ? ltext(q.stem).slice(0, 80) + (ltext(q.stem).length > 80 ? '…' : '') : ans.questionId
      return { ...ans, stem }
    })
})

function formatAnswerDisplay(q: Question, answer: unknown): string {
  if (answer == null) return '(none)'

  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
      if (typeof answer === 'number') {
        const opt = q.options[answer]
        return opt ? `${String.fromCharCode(65 + answer)}. ${ltext(opt)}` : String(answer)
      }
      return String(answer)
    case 'multi':
      if (Array.isArray(answer)) {
        return (answer as number[])
          .map((i) => {
            const opt = q.options[i]
            return opt ? `${String.fromCharCode(65 + i)}. ${ltext(opt)}` : String(i)
          })
          .join(', ')
      }
      return String(answer)
    case 'matching':
    case 'enhanced-matching':
      if (Array.isArray(answer)) {
        return q.left
          .map((left, i) => {
            const rightIdx = (answer as number[])[i]
            const right = q.right[rightIdx]
            return `${ltext(left)} → ${right ? ltext(right) : '?'}`
          })
          .join('; ')
      }
      return String(answer)
    case 'hotspot':
      if (Array.isArray(answer)) {
        return (answer as string[])
          .map((id) => {
            const region = q.regions.find((r) => r.id === id)
            return region ? ltext(region.label) : id
          })
          .join(', ')
      }
      return String(answer)
    case 'pulldown':
      if (typeof answer === 'object' && answer !== null) {
        return q.blanks
          .map((b) => {
            const sel = (answer as Record<string, number>)[b.id]
            const opt = sel !== undefined ? b.options[sel] : undefined
            return opt ? ltext(opt) : '?'
          })
          .join('; ')
      }
      return String(answer)
    default:
      return String(answer)
  }
}

function getCorrectAnswer(q: Question): unknown {
  switch (q.type) {
    case 'mcq':
    case 'graphic-mcq':
    case 'multi':
    case 'matching':
    case 'enhanced-matching':
    case 'hotspot':
      return q.correct
    case 'pulldown':
      return Object.fromEntries(q.blanks.map((b) => [b.id, b.correct]))
    default:
      return undefined
  }
}

const wrongQuestions = computed(() =>
  answers.value
    .filter((a) => !a.correct)
    .slice(0, 10)
    .map((ans) => {
      const q = questions.value.get(ans.questionId)
      if (!q) {
        return {
          stem: ans.questionId,
          chosenAnswer: String(ans.given ?? ''),
          correctAnswer: '',
        }
      }
      return {
        stem: ltext(q.stem),
        chosenAnswer: formatAnswerDisplay(q, ans.given),
        correctAnswer: formatAnswerDisplay(q, getCorrectAnswer(q)),
      }
    }),
)
function modeIcon(mode: string): string {
  const map: Record<string, string> = {
    real: '🎯',
    'full-untimed': '📋',
    free: '♾️',
    custom: '⚙️',
  }
  return map[mode] ?? '📝'
}

async function retryWeakAreas(): Promise<void> {
  if (!score.value) return

  const weakDomains = (Object.entries(score.value.byDomain) as [Domain, { correct: number; total: number }][])
    .filter(([, s]) => s.total > 0 && (s.correct / s.total) * 100 < EXAM.PASS_PROXY_PCT)
    .map(([d]) => d)

  const weakTasks = Object.entries(score.value.byTask)
    .filter(([, s]) => s.total > 0 && (s.correct / s.total) * 100 < EXAM.PASS_PROXY_PCT)
    .map(([task]) => task)

  const query: Record<string, string> = { mode: 'custom' }
  if (weakDomains.length > 0) query.domains = weakDomains.join(',')
  if (weakTasks.length > 0) query.tasks = weakTasks.join(',')

  router.push({ path: '/mode', query })
}

function savePdf(): void {
  window.print()
}

function goReview(): void {
  router.push(`/review/${attemptId.value}`)
}

const confettiParticles = Array.from({ length: 50 }, (_, i) => ({
  id: i,
  left: `${Math.random() * 100}%`,
  delay: `${Math.random() * 2}s`,
  duration: `${2 + Math.random() * 2}s`,
  color: ['#4f46e5', '#16a34a', '#d97706', '#dc2626', '#0d9488'][i % 5],
}))
</script>

<template>
  <div class="results-page mx-auto max-w-5xl px-4 pb-24 pt-6">
    <p v-if="loading" class="text-on-surface-muted">{{ t('common.loading') }}</p>

    <template v-else-if="attempt && score">
      <!-- Confetti -->
      <div v-if="showConfetti" class="confetti-container pointer-events-none fixed inset-0 z-50 overflow-hidden">
        <span
          v-for="p in confettiParticles"
          :key="p.id"
          class="confetti-particle absolute top-0 h-2 w-2 rounded-sm"
          :style="{
            left: p.left,
            backgroundColor: p.color,
            animationDelay: p.delay,
            animationDuration: p.duration,
          }"
        />
      </div>

      <!-- Verdict card -->
      <div
        class="relative mb-6 overflow-hidden rounded-2xl p-8 text-center shadow-lg"
        :class="passed ? 'bg-success text-white' : 'bg-surface-raised border-2 border-danger'"
      >
        <p class="text-sm opacity-80">{{ modeIcon(attempt.mode) }} {{ attempt.mode }}</p>
        <h1
          class="mt-2 text-3xl font-black tracking-wide sm:text-4xl"
          :class="passed ? '' : 'text-danger'"
        >
          {{ passed ? t('results.passed') : t('results.failed') }}
        </h1>
        <p v-if="isPartial" class="mt-2 text-sm opacity-80">
          {{ t('results.partial', { n: answers.length, total: score.max }) }}
        </p>
      </div>

      <!-- Score -->
      <div class="mb-6 rounded-2xl border border-border bg-surface-raised p-6 text-center">
        <p class="text-sm text-on-surface-muted">{{ t('results.score') }}</p>
        <p class="text-5xl font-bold text-on-surface">{{ pct }}%</p>
        <p class="mt-1 text-xs text-on-surface-muted">
          {{ t('results.proxy', { pct: EXAM.PASS_PROXY_PCT }) }}
        </p>
        <p class="mt-3 text-sm text-on-surface-muted">
          {{ score.raw }} / {{ score.max }}
          · {{ t('results.duration') }}: {{ formatDuration(attempt.durationSec) }}
        </p>
      </div>

      <!-- Domain bands -->
      <section class="mb-6">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">
          {{ t('results.domainPerformance') }}
        </h2>
        <div class="grid gap-3 sm:grid-cols-3">
          <div
            v-for="domain in ['people', 'process', 'business']"
            :key="domain"
            class="rounded-xl border border-border bg-surface-raised p-4"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-on-surface">{{ domainLabel(domain) }}</span>
              <span
                v-if="domainBands[domain]"
                class="rounded-full border px-2.5 py-0.5 text-xs font-bold"
                :class="bandClasses(domainBands[domain])"
              >
                {{ domainBands[domain] }}
              </span>
            </div>
            <p class="mt-2 text-2xl font-bold text-on-surface">{{ domainPct(domain) }}%</p>
            <p class="text-xs text-on-surface-muted">{{ bandLabel(domainBands[domain] ?? computeBand(domainPct(domain))) }}</p>
          </div>
        </div>
      </section>

      <!-- Charts -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('results.byTask') }}</h2>
        <HorizontalBarChart :labels="taskChart.labels" :values="taskChart.values" />
      </section>

      <div class="mb-6 grid gap-6 sm:grid-cols-2">
        <section class="rounded-2xl border border-border bg-surface-raised p-5">
          <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('results.byType') }}</h2>
          <HorizontalBarChart :labels="typeChart.labels" :values="typeChart.values" />
        </section>
        <section class="rounded-2xl border border-border bg-surface-raised p-5">
          <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('results.byApproach') }}</h2>
          <HorizontalBarChart :labels="approachChart.labels" :values="approachChart.values" />
        </section>
      </div>

      <!-- Time analysis -->
      <section class="mb-6 rounded-2xl border border-border bg-surface-raised p-5">
        <h2 class="mb-3 text-lg font-semibold text-on-surface">{{ t('results.timeAnalysis') }}</h2>
        <div class="mb-4 grid grid-cols-2 gap-4">
          <div>
            <p class="text-xs text-on-surface-muted">{{ t('results.duration') }}</p>
            <p class="text-xl font-bold text-on-surface">{{ formatDuration(attempt.durationSec) }}</p>
          </div>
          <div>
            <p class="text-xs text-on-surface-muted">{{ t('results.avgTime') }}</p>
            <p class="text-xl font-bold text-on-surface">{{ avgTimeSec }}s</p>
          </div>
        </div>
        <h3 class="mb-2 text-sm font-medium text-on-surface">{{ t('results.slowest') }}</h3>
        <ul class="space-y-2">
          <li
            v-for="(item, idx) in slowestQuestions"
            :key="item.id"
            class="flex items-start gap-2 rounded-lg bg-surface-alt px-3 py-2 text-sm"
          >
            <span class="shrink-0 font-mono text-on-surface-muted">{{ idx + 1 }}.</span>
            <span class="flex-1 text-on-surface">{{ item.stem }}</span>
            <span class="shrink-0 font-mono text-warning">{{ item.timeSec }}s</span>
          </li>
        </ul>
      </section>

      <WeakPointCard
        v-if="score"
        class="mb-6 print:hidden"
        :attempt-id="attemptId"
        :score="score"
        :wrong-questions="wrongQuestions"
        :initial-ai-summary="attempt.aiSummary"
      />

      <!-- Actions -->
      <div class="flex flex-col gap-3 sm:flex-row print:hidden">
        <button
          type="button"
          class="flex-1 rounded-2xl bg-primary px-6 py-3 font-semibold text-white transition hover:bg-primary-dark"
          @click="goReview"
        >
          {{ t('results.reviewAnswers') }}
        </button>
        <button
          type="button"
          class="flex-1 rounded-2xl border border-border bg-surface-raised px-6 py-3 font-semibold text-on-surface transition hover:bg-surface-alt"
          @click="retryWeakAreas"
        >
          {{ t('results.retryWeak') }}
        </button>
        <button
          type="button"
          class="rounded-2xl border border-border bg-surface-raised px-6 py-3 font-semibold text-on-surface transition hover:bg-surface-alt"
          @click="savePdf"
        >
          {{ t('results.savePdf') }}
        </button>
      </div>
    </template>

    <p v-else class="text-on-surface-muted">{{ t('history.empty') }}</p>
  </div>
</template>

<style scoped>
.confetti-particle {
  animation: confetti-fall linear forwards;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-10px) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

@media print {
  .results-page {
    padding: 0;
  }
}
</style>
