<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { db } from '@/db/index'
import { loadAllQuestions } from '@/core/bank/loader'
import { useExamSessionStore } from '@/stores/examSession'
import type { ExamConfig, Question } from '@/core/types'

const { t } = useI18n()
const router = useRouter()
const session = useExamSessionStore()

const bookmarkCount = ref(0)
const loading = ref(false)

onMounted(async () => {
  bookmarkCount.value = await db.bookmarks.count()
})

async function reviewBookmarks(): Promise<void> {
  if (bookmarkCount.value === 0) return
  loading.value = true
  try {
    const [bookmarks, allQuestions] = await Promise.all([
      db.bookmarks.orderBy('savedAt').reverse().toArray(),
      loadAllQuestions(),
    ])

    const idSet = new Set(bookmarks.map((b) => b.questionId))
    const questions: Question[] = allQuestions.filter((q) => idSet.has(q.id))

    if (questions.length === 0) return

    const config: ExamConfig = {
      mode: 'custom',
      questionCount: questions.length,
      timerMode: 'off',
      feedbackMode: 'immediate',
      filters: {},
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
    :disabled="loading || bookmarkCount === 0"
    @click="reviewBookmarks"
  >
    <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-warning/10 text-2xl">🔖</span>
    <div class="min-w-0 flex-1">
      <p class="font-semibold text-on-surface">{{ t('srs.bookmarks') }}</p>
      <p class="text-sm text-on-surface-muted">
        {{ bookmarkCount > 0 ? t('srs.bookmarksCount', { count: bookmarkCount }) : t('srs.bookmarksEmpty') }}
      </p>
    </div>
    <span v-if="bookmarkCount > 0" class="text-on-surface-muted">{{ loading ? '…' : '→' }}</span>
  </button>
</template>
