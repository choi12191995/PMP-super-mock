<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ECO_TASKS } from '@/core/examConstants'

export interface TaskHeatmapPoint {
  task: string
  accuracy: number
  total: number
}

const props = defineProps<{
  data: TaskHeatmapPoint[]
}>()

const emit = defineEmits<{
  select: [task: string]
}>()

const { t } = useI18n()

const allTasks = computed(() => {
  const tasks: { id: string; name: string }[] = []
  for (const group of Object.values(ECO_TASKS)) {
    for (const task of group) {
      tasks.push({ id: task.id, name: task.name })
    }
  }
  return tasks
})

const dataMap = computed(() => {
  const map = new Map<string, TaskHeatmapPoint>()
  for (const point of props.data) {
    map.set(point.task, point)
  }
  return map
})

function cellColor(taskId: string): string {
  const point = dataMap.value.get(taskId)
  if (!point || point.total === 0) return 'bg-border/40'
  const acc = point.accuracy
  if (acc >= 75) return 'bg-success/80 hover:bg-success'
  if (acc >= 50) return 'bg-warning/70 hover:bg-warning'
  return 'bg-danger/70 hover:bg-danger'
}

function cellTitle(taskId: string, name: string): string {
  const point = dataMap.value.get(taskId)
  if (!point || point.total === 0) return t('dashboard.taskUnseen', { id: taskId, name })
  return t('dashboard.taskTooltip', {
    id: taskId,
    name,
    pct: Math.round(point.accuracy),
    total: point.total,
  })
}

function onSelect(taskId: string): void {
  emit('select', taskId)
}
</script>

<template>
  <div class="grid grid-cols-4 gap-1.5 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-13">
    <button
      v-for="task in allTasks"
      :key="task.id"
      type="button"
      class="group relative flex aspect-square min-h-[36px] items-center justify-center rounded-md text-[10px] font-bold text-white transition active:scale-95"
      :class="cellColor(task.id)"
      :title="cellTitle(task.id, task.name)"
      @click="onSelect(task.id)"
    >
      <span class="drop-shadow-sm">{{ task.id }}</span>
    </button>
  </div>
</template>
