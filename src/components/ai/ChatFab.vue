<script setup lang="ts">
import { onMounted, ref } from 'vue'

defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const hasPulsed = ref(false)

onMounted(() => {
  const seen = localStorage.getItem('ai-fab-seen')
  if (!seen) {
    hasPulsed.value = true
    localStorage.setItem('ai-fab-seen', '1')
    setTimeout(() => {
      hasPulsed.value = false
    }, 3000)
  }
})
</script>

<template>
  <button
    v-if="visible"
    type="button"
    class="chat-fab fixed bottom-36 right-4 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-lg transition hover:bg-primary-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary md:bottom-8 md:right-8"
    :class="{ 'chat-fab-pulse': hasPulsed }"
    aria-label="AI Assistant"
    @click="emit('toggle')"
  >
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6">
      <path
        fill-rule="evenodd"
        d="M4.848 2.771A49.144 49.144 0 0112 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 01-3.476.383.39.39 0 00-.297.17l-2.755 4.133a.75.75 0 01-1.248 0l-2.755-4.133a.39.39 0 00-.297-.17 48.9 48.9 0 01-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97zM6.75 8.25a.75.75 0 01.75-.75h9a.75.75 0 010 1.5h-9a.75.75 0 01-.75-.75zm.75 2.25a.75.75 0 000 1.5H12a.75.75 0 000-1.5H7.5z"
        clip-rule="evenodd"
      />
    </svg>
  </button>
</template>

<style scoped>
.chat-fab-pulse {
  animation: fab-pulse 2s ease-in-out infinite;
}

@keyframes fab-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgb(79 70 229 / 0.5);
  }
  50% {
    box-shadow: 0 0 0 12px rgb(79 70 229 / 0);
  }
}
</style>
