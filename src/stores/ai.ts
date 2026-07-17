import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { streamChat, testConnection, fetchModels, type ChatMessage, type AiConfig } from '@/core/ai/client'
import { buildQuestionPrompt } from '@/core/ai/prompts'
import type { QuestionBase } from '@/core/types'
import type { ExamMode } from '@/stores/examSession'

export type AiReplyLanguage = 'auto' | 'en' | 'zh-TW'

export interface QuestionContext {
  question: QuestionBase
  userAnswer?: unknown
  correctAnswer?: unknown
  isAnswered: boolean
  language: 'en' | 'zh-TW'
}

interface StoredAiConfig {
  baseURL?: string
  apiKey?: string
  model?: string
  temperature?: number
  enabled?: boolean
  replyLanguage?: AiReplyLanguage
  chatEnabledByMode?: Partial<Record<ExamMode, boolean>>
}

const STORAGE_KEY = 'ai'

const DEFAULT_CHAT_BY_MODE: Record<ExamMode, boolean> = {
  real: false,
  'full-untimed': true,
  free: true,
  custom: true,
}

export const useAiStore = defineStore('ai', () => {
  const baseURL = ref('https://api.openai.com/v1')
  const apiKey = ref('')
  const model = ref('gpt-4o-mini')
  const temperature = ref(0.7)
  const enabled = ref(false)
  const replyLanguage = ref<AiReplyLanguage>('auto')
  const chatEnabledByMode = ref<Record<ExamMode, boolean>>({ ...DEFAULT_CHAT_BY_MODE })

  const chatMessages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const currentQuestionId = ref<string | null>(null)
  const lastError = ref<string | null>(null)

  let abortController: AbortController | null = null

  const isConfigured = computed(() => baseURL.value.trim().length > 0 && apiKey.value.trim().length > 0)

  const aiConfig = computed(
    (): AiConfig => ({
      baseURL: baseURL.value.trim(),
      apiKey: apiKey.value.trim(),
      model: model.value.trim(),
      temperature: temperature.value,
    }),
  )

  function loadConfig(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return
      const stored = JSON.parse(raw) as StoredAiConfig
      if (stored.baseURL != null) baseURL.value = stored.baseURL
      if (stored.apiKey != null) apiKey.value = stored.apiKey
      if (stored.model != null) model.value = stored.model
      if (stored.temperature != null) temperature.value = stored.temperature
      if (stored.enabled != null) enabled.value = stored.enabled
      if (stored.replyLanguage != null) replyLanguage.value = stored.replyLanguage
      if (stored.chatEnabledByMode) {
        chatEnabledByMode.value = { ...DEFAULT_CHAT_BY_MODE, ...stored.chatEnabledByMode }
      }
    } catch {
      /* ignore corrupt storage */
    }
  }

  function saveConfig(): void {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        baseURL: baseURL.value,
        apiKey: apiKey.value,
        model: model.value,
        temperature: temperature.value,
        enabled: enabled.value,
        replyLanguage: replyLanguage.value,
        chatEnabledByMode: chatEnabledByMode.value,
      }),
    )
  }

  function resolveLanguage(uiLang: 'en' | 'zh-TW'): 'en' | 'zh-TW' {
    if (replyLanguage.value === 'auto') return uiLang
    return replyLanguage.value
  }

  function isChatEnabledForMode(mode: ExamMode): boolean {
    return chatEnabledByMode.value[mode] ?? false
  }

  function switchQuestion(questionId: string): void {
    if (currentQuestionId.value !== questionId) {
      clearChat()
      currentQuestionId.value = questionId
    }
  }

  function clearChat(): void {
    stopStreaming()
    chatMessages.value = []
    lastError.value = null
  }

  function stopStreaming(): void {
    abortController?.abort()
    abortController = null
    isStreaming.value = false
  }

  async function sendMessage(content: string, questionContext: QuestionContext): Promise<void> {
    if (!isConfigured.value || !enabled.value) return

    lastError.value = null
    switchQuestion(questionContext.question.id)

    const lang = resolveLanguage(questionContext.language)
    const systemMessages = buildQuestionPrompt({
      question: questionContext.question,
      userAnswer: questionContext.userAnswer,
      correctAnswer: questionContext.correctAnswer,
      isAnswered: questionContext.isAnswered,
      language: lang,
    })

    const userMsg: ChatMessage = { role: 'user', content }
    chatMessages.value.push(userMsg)

    const assistantMsg: ChatMessage = { role: 'assistant', content: '' }
    chatMessages.value.push(assistantMsg)

    const history = chatMessages.value.slice(0, -1)
    const messages: ChatMessage[] = [...systemMessages.slice(0, 1)]
    const contextUser = systemMessages[1]
    if (contextUser) messages.push(contextUser)
    for (const msg of history) {
      if (msg.role === 'user' || msg.role === 'assistant') messages.push(msg)
    }

    abortController = new AbortController()
    isStreaming.value = true

    try {
      for await (const chunk of streamChat(aiConfig.value, messages, abortController.signal)) {
        assistantMsg.content += chunk
        chatMessages.value = [...chatMessages.value]
      }
    } catch (err) {
      if (abortController?.signal.aborted) {
        if (!assistantMsg.content) {
          chatMessages.value = chatMessages.value.slice(0, -1)
        }
        return
      }
      lastError.value = err instanceof Error ? err.message : 'Unknown error'
      if (!assistantMsg.content) {
        chatMessages.value = chatMessages.value.slice(0, -1)
      }
    } finally {
      isStreaming.value = false
      abortController = null
    }
  }

  async function runTestConnection(): Promise<{ ok: boolean; error?: string }> {
    return testConnection(aiConfig.value)
  }

  async function loadModels(): Promise<string[]> {
    return fetchModels(baseURL.value.trim(), apiKey.value.trim())
  }

  loadConfig()

  return {
    baseURL,
    apiKey,
    model,
    temperature,
    enabled,
    replyLanguage,
    chatEnabledByMode,
    chatMessages,
    isStreaming,
    currentQuestionId,
    lastError,
    isConfigured,
    aiConfig,
    loadConfig,
    saveConfig,
    resolveLanguage,
    isChatEnabledForMode,
    sendMessage,
    stopStreaming,
    clearChat,
    switchQuestion,
    runTestConnection,
    loadModels,
  }
})
