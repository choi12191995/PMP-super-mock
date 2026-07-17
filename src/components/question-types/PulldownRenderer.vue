<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PulldownQ, LText } from '@/core/types'

const props = defineProps<{
  question: PulldownQ
  modelValue: Record<string, number>
  showFeedback: boolean
  correctAnswer: Record<string, number>
  disabled: boolean
  lang: 'en' | 'zh-TW'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, number>]
}>()

const { t } = useI18n()

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

type StemPart =
  | { kind: 'text'; content: string }
  | { kind: 'blank'; id: string }

const stemParts = computed((): StemPart[] => {
  const stem = ltext(props.question.stem)
  const parts: StemPart[] = []
  const regex = /\{\{(b\d+)\}\}/g
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = regex.exec(stem)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ kind: 'text', content: stem.slice(lastIndex, match.index) })
    }
    parts.push({ kind: 'blank', id: match[1] })
    lastIndex = regex.lastIndex
  }

  if (lastIndex < stem.length) {
    parts.push({ kind: 'text', content: stem.slice(lastIndex) })
  }

  return parts
})

function blankById(id: string) {
  return props.question.blanks.find((b) => b.id === id)
}

function selectClasses(blankId: string): string[] {
  const selected = props.modelValue[blankId]
  const blank = blankById(blankId)
  if (!blank) return ['border-border bg-surface-raised']

  const isCorrect = props.showFeedback && selected === props.correctAnswer[blankId]
  const isWrong =
    props.showFeedback && selected !== undefined && selected !== props.correctAnswer[blankId]

  const classes = [
    'mx-1 inline-block min-h-[44px] max-w-full rounded-lg border-2 px-2 py-1.5 text-sm font-medium transition',
  ]

  if (isCorrect) classes.push('border-success bg-success/10 text-success')
  else if (isWrong) classes.push('border-danger bg-danger/10 text-danger')
  else classes.push('border-border bg-surface-raised text-on-surface')

  if (props.disabled && !props.showFeedback) classes.push('pointer-events-none opacity-70')

  return classes
}

function onSelect(blankId: string, event: Event): void {
  const target = event.target as HTMLSelectElement
  const value = Number(target.value)
  if (Number.isNaN(value)) return

  emit('update:modelValue', {
    ...props.modelValue,
    [blankId]: value,
  })
}
</script>

<template>
  <div class="space-y-5">
    <p
      class="inline-flex rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary"
    >
      {{ t('exam.pulldownInstruction') }}
    </p>

    <p class="text-base leading-relaxed text-on-surface">
      <template v-for="(part, index) in stemParts" :key="index">
        <span v-if="part.kind === 'text'" class="whitespace-pre-wrap">{{ part.content }}</span>
        <select
          v-else
          :value="modelValue[part.id] ?? ''"
          :class="selectClasses(part.id)"
          :disabled="disabled && !showFeedback"
          :aria-label="`${t('exam.pulldownInstruction')} ${part.id}`"
          @change="onSelect(part.id, $event)"
        >
          <option value="" disabled>
            {{ lang === 'zh-TW' ? '選擇…' : 'Select…' }}
          </option>
          <option
            v-for="(option, optIndex) in blankById(part.id)?.options ?? []"
            :key="optIndex"
            :value="optIndex"
          >
            {{ ltext(option) }}
          </option>
        </select>
      </template>
    </p>
  </div>
</template>
