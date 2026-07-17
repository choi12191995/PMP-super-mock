import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ExamMode = 'real' | 'full-untimed' | 'free' | 'custom'
export type SessionState =
  | 'configuring'
  | 'running'
  | 'breakOffered'
  | 'onBreak'
  | 'reviewingSection'
  | 'paused'
  | 'submitted'
  | 'scored'
  | 'quit'

export const useExamSessionStore = defineStore('examSession', () => {
  const state = ref<SessionState>('configuring')
  const mode = ref<ExamMode>('free')
  const isInProgress = ref(false)

  function setState(s: SessionState) {
    state.value = s
    isInProgress.value = ['running', 'breakOffered', 'onBreak', 'reviewingSection', 'paused'].includes(s)
  }

  function reset() {
    state.value = 'configuring'
    isInProgress.value = false
  }

  return { state, mode, isInProgress, setState, reset }
})
