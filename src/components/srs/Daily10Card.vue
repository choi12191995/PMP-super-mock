<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db } from '@/db/index'
import { loadAllQuestions } from '@/core/bank/loader'
import { getDueQuestionIds, pickDaily10Questions } from '@/core/srs/index'
import { useExamSessionStore } from '@/stores/examSession'
import type { ExamConfig, Question } from '@/core/types'

const { t } = useI18n()
const router = useRouter()
const session = useExamSessionStore()

const dueCount = ref(0)
const loading = ref(false)

onMounted(async () => {
  const due = await getDueQuestionIds()
  dueCount.value = due.length
})

async function startDaily10(): Promise<void> {
  loading.value = true
  try {
    const [allQuestions, dueIds, answers] = await Promise.all([
      loadAllQuestions(),
      getDueQuestionIds(),
      db.answers.toArray(),
    ])

    const seenIds = new Set(
      answers.map((a) => a.questionId.replace(/__dup\d+$/, '').replace(/__fill\d+$/, '')),
    )

    const pickedIds = pickDaily10Questions(allQuestions, dueIds, seenIds, 10)
    const idSet = new Set(pickedIds)
    const questions: Question[] = allQuestions.filter((q) => idSet.has(q.id))

    if (questions.length === 0) return

    const config: ExamConfig = {
      mode: 'custom',
      questionCount: questions.length,
      timerMode: 'off',
      feedbackMode: 'immediate',
      filters: { domains: ['people', 'process', 'business'] },
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
    class="flex w-full items-center gap-4 rounded-2xl border border-border bg-surface-raised p-4 text-left transition hover:border-primary/50 active:scale-[0.99] disabled:opacity-50"
    :disabled="loading"
    @click="startDaily10"
  >
    <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-2xl">📅</span>
    <div class="min-w-0 flex-1">
      <p class="font-semibold text-on-surface">{{ t('srs.daily10') }}</p>
      <p class="text-sm text-on-surface-muted">{{ t('srs.daily10Desc') }}</p>
      <p v-if="dueCount > 0" class="mt-1 text-xs text-primary">
        {{ t('srs.dueCount', { count: dueCount }) }}
      </p>
    </div>
    <span class="text-on-surface-muted">{{ loading ? '…' : '→' }}</span>
  </button>
</template>
