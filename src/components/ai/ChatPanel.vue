<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAiStore, type QuestionContext } from '@/stores/ai'

const props = defineProps<{
  visible: boolean
  questionContext: QuestionContext | null
}>()

const emit = defineEmits<{
  close: []
}>()

const { t, locale } = useI18n()
const ai = useAiStore()

const inputText = ref('')
const messagesEl = ref<HTMLElement | null>(null)
const showCostNote = ref(false)
const lastFailedMessage = ref<string | null>(null)

const uiLang = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en') as 'en' | 'zh-TW')

const chips = computed(() => {
  const base = [
    { key: 'explain', text: t('ai.chips.explain') },
    { key: 'terms', text: t('ai.chips.terms') },
    { key: 'whyWrong', text: t('ai.chips.whyWrong') },
    { key: 'tip', text: t('ai.chips.tip') },
  ]
  if (uiLang.value === 'en') {
    base.push({ key: 'zhExplain', text: t('ai.chips.zhExplain') })
  } else {
    base.push({ key: 'enExplain', text: 'Explain in English' })
  }
  return base
})

function renderMarkdown(text: string): string {
  const raw = marked.parse(text, { async: false }) as string
  return DOMPurify.sanitize(raw)
}

function scrollToBottom(): void {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

watch(
  () => ai.chatMessages.length,
  () => scrollToBottom(),
)

watch(
  () => ai.chatMessages[ai.chatMessages.length - 1]?.content,
  () => scrollToBottom(),
)

watch(
  () => props.visible,
  (open) => {
    if (open && !localStorage.getItem('ai-cost-note-seen')) {
      showCostNote.value = true
      localStorage.setItem('ai-cost-note-seen', '1')
    }
  },
)

async function send(text: string): Promise<void> {
  if (!text.trim() || !props.questionContext || ai.isStreaming) return

  const msg = text.trim()
  inputText.value = ''
  lastFailedMessage.value = null

  try {
    await ai.sendMessage(msg, props.questionContext)
    if (ai.lastError) lastFailedMessage.value = msg
  } catch {
    lastFailedMessage.value = msg
  }
}

function onChip(chip: { key: string; text: string }): void {
  if (chip.key === 'zhExplain') {
    void send('請用繁體中文解釋這道題目')
  } else if (chip.key === 'enExplain') {
    void send('Explain this question in English')
  } else {
    void send(chip.text)
  }
}

async function retry(): Promise<void> {
  if (!lastFailedMessage.value) return
  const msg = lastFailedMessage.value
  lastFailedMessage.value = null
  ai.lastError = null
  await send(msg)
}

function onSubmit(): void {
  void send(inputText.value)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-end justify-end md:items-stretch"
    >
      <div
        class="absolute inset-0 bg-black/40"
        @click="emit('close')"
      />

      <aside
        class="glass-modal relative flex h-[75vh] w-full flex-col md:h-full md:max-h-none md:w-[420px] md:rounded-none md:border-l md:border-t-0"
      >
        <header class="flex shrink-0 items-center justify-between border-b border-border px-4 py-3">
          <h2 class="text-lg font-semibold text-on-surface">{{ t('ai.chatTitle') }}</h2>
          <button
            type="button"
            class="rounded-lg p-2 text-on-surface-muted hover:bg-surface-alt"
            :aria-label="t('common.close')"
            @click="emit('close')"
          >
            ✕
          </button>
        </header>

        <p
          v-if="showCostNote"
          class="shrink-0 border-b border-border bg-primary/5 px-4 py-2 text-xs text-on-surface-muted"
        >
          {{ t('ai.costNote') }}
        </p>

        <div class="shrink-0 flex gap-2 overflow-x-auto border-b border-border px-4 py-2">
          <button
            v-for="chip in chips"
            :key="chip.key"
            type="button"
            class="shrink-0 rounded-full border border-border bg-surface-alt px-3 py-1.5 text-xs font-medium text-on-surface transition hover:border-primary hover:text-primary disabled:opacity-50"
            :disabled="ai.isStreaming || !questionContext"
            @click="onChip(chip)"
          >
            {{ chip.text }}
          </button>
        </div>

        <div
          ref="messagesEl"
          class="flex-1 overflow-y-auto px-4 py-3"
        >
          <p
            v-if="!ai.isConfigured"
            class="text-sm text-on-surface-muted"
          >
            {{ t('ai.notConfigured') }}
          </p>

          <div
            v-for="(msg, idx) in ai.chatMessages"
            :key="idx"
            class="mb-3"
            :class="msg.role === 'user' ? 'text-right' : 'text-left'"
          >
            <div
              class="inline-block max-w-[90%] rounded-2xl px-4 py-2 text-sm"
              :class="
                msg.role === 'user'
                  ? 'bg-primary text-white'
                  : 'border border-border bg-surface-alt text-on-surface prose prose-sm max-w-none dark:prose-invert'
              "
            >
              <span v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</span>
              <div
                v-else-if="msg.content"
                v-html="renderMarkdown(msg.content)"
              />
              <span
                v-else-if="ai.isStreaming"
                class="text-on-surface-muted"
              >{{ t('ai.sending') }}</span>
            </div>
          </div>

          <div
            v-if="ai.lastError"
            class="rounded-xl border border-danger/30 bg-danger/10 p-3 text-sm text-danger"
          >
            <p>{{ t('ai.error', { msg: ai.lastError }) }}</p>
            <button
              type="button"
              class="mt-2 font-medium underline"
              @click="retry"
            >
              {{ t('ai.retry') }}
            </button>
          </div>
        </div>

        <footer class="shrink-0 border-t border-border p-3">
          <div class="flex gap-2">
            <input
              v-model="inputText"
              type="text"
              class="min-h-[44px] flex-1 rounded-xl border border-border bg-surface px-3 text-sm text-on-surface outline-none focus:border-primary"
              :placeholder="t('ai.placeholder')"
              :disabled="ai.isStreaming || !questionContext || !ai.isConfigured"
              @keydown.enter="onSubmit"
            />
            <button
              v-if="ai.isStreaming"
              type="button"
              class="min-h-[44px] shrink-0 rounded-xl border border-danger px-4 text-sm font-semibold text-danger"
              @click="ai.stopStreaming()"
            >
              {{ t('ai.stop') }}
            </button>
            <button
              v-else
              type="button"
              class="min-h-[44px] shrink-0 rounded-xl bg-primary px-4 text-sm font-semibold text-white disabled:opacity-50"
              :disabled="!inputText.trim() || !questionContext || !ai.isConfigured"
              @click="onSubmit"
            >
              →
            </button>
          </div>
        </footer>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
:deep(.prose p) {
  margin: 0.25em 0;
}

:deep(.prose ul) {
  margin: 0.25em 0;
  padding-left: 1.25em;
}
</style>
