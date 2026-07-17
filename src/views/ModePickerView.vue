<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { loadAllQuestions } from '@/core/bank/loader'
import { EXAM } from '@/core/examConstants'
import { useExamSessionStore } from '@/stores/examSession'
import type { Difficulty, Domain, ExamConfig, Question, QType } from '@/core/types'

type ModeKey = ExamConfig['mode']

const router = useRouter()
const { t } = useI18n()
const session = useExamSessionStore()

const selectedMode = ref<ModeKey>('free')
const loading = ref(false)
const error = ref<string | null>(null)

const domains = ref<Domain[]>(['people', 'process', 'business'])
const difficulties = ref<Difficulty[]>([1, 2, 3])
const questionCount = ref(20)
const timerMode = ref<ExamConfig['timerMode']>('off')
const feedbackMode = ref<ExamConfig['feedbackMode']>('immediate')

const modes: { key: ModeKey; icon: string }[] = [
  { key: 'real', icon: '🎯' },
  { key: 'full-untimed', icon: '📋' },
  { key: 'free', icon: '♾️' },
  { key: 'custom', icon: '⚙️' },
]

const showFreeFilters = computed(() => selectedMode.value === 'free' || selectedMode.value === 'custom')
const canStart = computed(() => !loading.value && domains.value.length > 0)

function selectMode(mode: ModeKey): void {
  selectedMode.value = mode

  switch (mode) {
    case 'real':
      questionCount.value = EXAM.TOTAL_QUESTIONS
      timerMode.value = 'countdown'
      feedbackMode.value = 'end'
      domains.value = ['people', 'process', 'business']
      difficulties.value = [1, 2, 3]
      break
    case 'full-untimed':
      questionCount.value = EXAM.TOTAL_QUESTIONS
      timerMode.value = 'count-up'
      feedbackMode.value = 'end'
      domains.value = ['people', 'process', 'business']
      difficulties.value = [1, 2, 3]
      break
    case 'free':
      questionCount.value = 9999
      timerMode.value = 'off'
      feedbackMode.value = 'immediate'
      break
    case 'custom':
      questionCount.value = 20
      timerMode.value = 'off'
      feedbackMode.value = 'end'
      break
  }
}

function toggleDomain(domain: Domain): void {
  const idx = domains.value.indexOf(domain)
  if (idx >= 0) {
    if (domains.value.length > 1) domains.value.splice(idx, 1)
  } else {
    domains.value.push(domain)
  }
}

function toggleDifficulty(d: Difficulty): void {
  const idx = difficulties.value.indexOf(d)
  if (idx >= 0) {
    if (difficulties.value.length > 1) difficulties.value.splice(idx, 1)
  } else {
    difficulties.value.push(d)
  }
}

function shuffle<T>(arr: T[]): T[] {
  const result = [...arr]
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

function filterQuestions(all: Question[]): Question[] {
  return all.filter((q) => {
    if (domains.value.length && !domains.value.includes(q.domain)) return false
    if (difficulties.value.length && !difficulties.value.includes(q.difficulty)) return false
    if (selectedMode.value === 'free' || selectedMode.value === 'custom') {
      const supported: QType[] = ['mcq', 'multi', 'graphic-mcq']
      if (!supported.includes(q.type)) return false
    }
    return true
  })
}

function buildConfig(filteredCount: number): ExamConfig {
  const count =
    selectedMode.value === 'free'
      ? filteredCount
      : Math.min(questionCount.value, filteredCount)

  const config: ExamConfig = {
    mode: selectedMode.value,
    questionCount: count,
    timerMode: timerMode.value,
    feedbackMode: feedbackMode.value,
    filters: {
      domains: [...domains.value],
      difficulties: [...difficulties.value],
    },
    onvue: false,
    aiChat: false,
  }

  if (timerMode.value === 'countdown') {
    config.timerSeconds =
      selectedMode.value === 'real'
        ? EXAM.DURATION_MINUTES * 60
        : questionCount.value * EXAM.PACE_SECONDS
  }

  return config
}

function modeTitle(mode: ModeKey): string {
  const map: Record<ModeKey, string> = {
    real: t('mode.realExam'),
    'full-untimed': t('mode.fullUntimed'),
    free: t('mode.free'),
    custom: t('mode.custom'),
  }
  return map[mode]
}

function modeDesc(mode: ModeKey): string {
  const map: Record<ModeKey, string> = {
    real: t('mode.realExamDesc'),
    'full-untimed': t('mode.fullUntimedDesc'),
    free: t('mode.freeDesc'),
    custom: t('mode.customDesc'),
  }
  return map[mode]
}

function difficultyLabel(d: Difficulty): string {
  if (d === 1) return t('common.easy')
  if (d === 2) return t('common.medium')
  return t('common.hard')
}

function domainLabel(d: Domain): string {
  const map: Record<Domain, string> = {
    people: t('common.people'),
    process: t('common.process'),
    business: t('common.business'),
  }
  return map[d]
}

async function startExam(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const all = await loadAllQuestions()
    const filtered = shuffle(filterQuestions(all))

    if (filtered.length === 0) {
      error.value = t('common.loading')
      return
    }

    const config = buildConfig(filtered.length)
    session.startSession(config, filtered)
    router.push('/exam')
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6">
    <h1 class="mb-2 text-2xl font-bold text-on-surface">{{ t('mode.title') }}</h1>
    <p class="mb-6 text-sm text-on-surface-muted">{{ t('app.tagline') }}</p>

    <!-- Mode cards -->
    <div class="mb-6 grid gap-3 sm:grid-cols-2">
      <button
        v-for="m in modes"
        :key="m.key"
        type="button"
        class="rounded-2xl border-2 p-5 text-left transition active:scale-[0.99]"
        :class="
          selectedMode === m.key
            ? 'border-primary bg-primary/5 shadow-md'
            : 'border-border bg-surface-raised hover:border-primary/50'
        "
        @click="selectMode(m.key)"
      >
        <div class="mb-2 flex items-center gap-2">
          <span class="text-2xl">{{ m.icon }}</span>
          <h2 class="text-lg font-semibold text-on-surface">{{ modeTitle(m.key) }}</h2>
        </div>
        <p class="text-sm leading-relaxed text-on-surface-muted">{{ modeDesc(m.key) }}</p>
      </button>
    </div>

    <!-- Filters (Free & Custom) -->
    <div
      v-if="showFreeFilters"
      class="mb-6 space-y-5 rounded-2xl border border-border bg-surface-raised p-5"
    >
      <h3 class="text-sm font-semibold uppercase tracking-wide text-on-surface-muted">
        {{ t('mode.filters') }}
      </h3>

      <div>
        <p class="mb-3 text-sm font-medium text-on-surface">{{ t('mode.domain') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="d in (['people', 'process', 'business'] as Domain[])"
            :key="d"
            type="button"
            class="min-h-[44px] rounded-xl border-2 px-4 py-2 text-sm font-medium transition"
            :class="
              domains.includes(d)
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-on-surface-muted hover:border-primary/40'
            "
            @click="toggleDomain(d)"
          >
            {{ domainLabel(d) }}
          </button>
        </div>
      </div>

      <div>
        <p class="mb-3 text-sm font-medium text-on-surface">{{ t('mode.difficulty') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="d in ([1, 2, 3] as Difficulty[])"
            :key="d"
            type="button"
            class="min-h-[44px] rounded-xl border-2 px-4 py-2 text-sm font-medium transition"
            :class="
              difficulties.includes(d)
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-on-surface-muted hover:border-primary/40'
            "
            @click="toggleDifficulty(d)"
          >
            {{ difficultyLabel(d) }}
          </button>
        </div>
      </div>

      <!-- Custom-only options -->
      <template v-if="selectedMode === 'custom'">
        <div>
          <label class="mb-2 block text-sm font-medium text-on-surface">
            {{ t('mode.questionCount') }}: {{ questionCount }}
          </label>
          <input
            v-model.number="questionCount"
            type="range"
            min="5"
            max="180"
            step="5"
            class="w-full accent-primary"
          />
        </div>

        <div>
          <p class="mb-3 text-sm font-medium text-on-surface">{{ t('mode.timer') }}</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tm in (['off', 'count-up', 'countdown'] as const)"
              :key="tm"
              type="button"
              class="min-h-[44px] rounded-xl border-2 px-4 py-2 text-sm font-medium transition"
              :class="
                timerMode === tm
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border text-on-surface-muted'
              "
              @click="timerMode = tm"
            >
              {{
                tm === 'off'
                  ? t('mode.timerOff')
                  : tm === 'count-up'
                    ? t('mode.timerCountUp')
                    : t('mode.timerPace', { seconds: EXAM.PACE_SECONDS })
              }}
            </button>
          </div>
        </div>

        <div>
          <p class="mb-3 text-sm font-medium text-on-surface">{{ t('mode.feedback') }}</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="fm in (['end', 'immediate'] as const)"
              :key="fm"
              type="button"
              class="min-h-[44px] rounded-xl border-2 px-4 py-2 text-sm font-medium transition"
              :class="
                feedbackMode === fm
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border text-on-surface-muted'
              "
              @click="feedbackMode = fm"
            >
              {{ fm === 'end' ? t('mode.feedbackEnd') : t('mode.feedbackImmediate') }}
            </button>
          </div>
        </div>
      </template>
    </div>

    <p v-if="error" class="mb-4 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
      {{ error }}
    </p>

    <button
      type="button"
      class="flex w-full min-h-[52px] items-center justify-center rounded-2xl bg-primary px-8 py-4 text-lg font-semibold text-white shadow-md transition hover:bg-primary-dark active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
      :disabled="!canStart"
      @click="startExam"
    >
      {{ loading ? t('common.loading') : t('mode.start') }}
    </button>
  </div>
</template>
