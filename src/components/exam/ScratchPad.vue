<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  visible: boolean
  modelValue: string
  questionId: string
}>()

const emit = defineEmits<{
  close: []
  'update:modelValue': [value: string]
}>()

const { t } = useI18n()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
      role="dialog"
      :aria-label="t('exam.scratchPad')"
      aria-modal="true"
    >
      <button
        type="button"
        class="absolute inset-0 bg-black/50"
        :aria-label="t('common.close')"
        @click="emit('close')"
      />

      <div
        class="relative flex h-[70vh] w-full max-w-lg flex-col rounded-t-2xl border border-border bg-surface-raised p-4 shadow-xl sm:h-auto sm:max-h-[80vh] sm:rounded-2xl"
      >
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-bold text-on-surface">{{ t('exam.scratchPad') }}</h2>
          <button
            type="button"
            class="touch-target rounded-xl px-3 py-2 text-sm font-medium text-on-surface-muted hover:bg-surface-alt"
            @click="emit('close')"
          >
            {{ t('common.close') }}
          </button>
        </div>

        <p class="mb-2 text-xs text-on-surface-muted">
          {{ t('exam.scratchPadHint', { id: questionId }) }}
        </p>

        <textarea
          :value="modelValue"
          class="min-h-[200px] flex-1 resize-none rounded-xl border border-border bg-surface px-4 py-3 text-sm leading-relaxed text-on-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          :placeholder="t('exam.scratchPadPlaceholder')"
          :aria-label="t('exam.scratchPad')"
          @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        />
      </div>
    </div>
  </Teleport>
</template>
