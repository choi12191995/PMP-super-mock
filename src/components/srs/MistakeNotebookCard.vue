<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getMistakeQuestionIds } from '@/core/srs/index'
import { loadAllQuestions } from '@/core/bank/loader'
import { useExamSessionStore } from '@/stores/examSession'
import type { ExamConfig, Question } from '@/core/types'

const { t } = useI18n()
const router = useRouter()
const session = useExamSessionStore()

const mistakeCount = ref(0)
const loading = ref(false)

onMounted(async () => {
  const ids = await getMistakeQuestionIds()
  mistakeCount.value = ids.length
})

async function reDrill(): Promise<void> {
  if (mistakeCount.value === 0) return
  loading.value = true
  try {
    const [ids, allQuestions] = await Promise.all([
      getMistakeQuestionIds(),
      loadAllQuestions(),
    ])

    const idSet = new Set(ids.slice(0, 20))
    const questions: Question[] = allQuestions.filter((q) => idSet.has(q.id))

    if (questions.length === 0) return

    const config: ExamConfig = {
      mode: 'custom',
      questionCount: questions.length,
      timerMode: 'off',
      feedbackMode: 'immediate',
      filters: { wrongOnly: true },
      onvue: false,
      aiChat: true,
    }

    session.startSession(config, questions)
    router.push('/exam')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <button
    type="button"
    class="glass-card flex w-full items-center gap-4 p-4 text-left transition active:scale-[0.99] disabled:opacity-50"
    :disabled="loading || mistakeCount === 0"
    @click="reDrill"
  >
    <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-danger/10 text-2xl">📕</span>
    <div class="min-w-0 flex-1">
      <p class="font-semibold text-on-surface">{{ t('srs.mistakes') }}</p>
      <p class="text-sm text-on-surface-muted">
        {{ mistakeCount > 0 ? t('srs.mistakesCount', { count: mistakeCount }) : t('srs.mistakesEmpty') }}
      </p>
    </div>
    <span v-if="mistakeCount > 0" class="text-on-surface-muted">{{ loading ? '…' : '→' }}</span>
  </button>
</template>
