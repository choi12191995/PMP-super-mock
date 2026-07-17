<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  total: number
  current: number
  answeredSet: Set<number>
  flaggedSet: Set<number>
  lockedSections?: Set<string>
  indexMap?: number[]
}>()

const emit = defineEmits<{
  navigate: [index: number]
}>()

const indices = computed(() => {
  if (props.indexMap && props.indexMap.length > 0) return props.indexMap
  return Array.from({ length: props.total }, (_, i) => i)
})

function questionNumber(localIdx: number): number {
  return localIdx + 1
}

function isAnswered(localIdx: number): boolean {
  const globalIdx = indices.value[localIdx] ?? localIdx
  return props.answeredSet.has(globalIdx)
}

function isFlagged(localIdx: number): boolean {
  const globalIdx = indices.value[localIdx] ?? localIdx
  return props.flaggedSet.has(globalIdx)
}

function cellClass(localIdx: number): string {
  if (localIdx === props.current) {
    return 'border-primary bg-primary text-white'
  }
  if (isAnswered(localIdx)) {
    return 'border-success bg-success/15 text-success'
  }
  return 'border-border bg-surface text-on-surface-muted'
}
</script>

<template>
  <div
    class="grid gap-2"
    :style="{ gridTemplateColumns: 'repeat(auto-fill, minmax(44px, 1fr))' }"
    role="navigation"
    :aria-label="'Question navigator'"
  >
    <button
      v-for="(_, localIdx) in total"
      :key="localIdx"
      type="button"
      class="relative flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg border-2 text-sm font-semibold transition hover:border-primary"
      :class="cellClass(localIdx)"
      @click="emit('navigate', localIdx)"
    >
      {{ questionNumber(localIdx) }}
      <span
        v-if="isFlagged(localIdx)"
        class="absolute -right-0.5 -top-0.5 text-[10px] text-warning"
        aria-hidden="true"
      >
        ▲
      </span>
    </button>
  </div>
</template>
