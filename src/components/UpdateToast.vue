<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useExamSessionStore } from '@/stores/examSession'

const { t } = useI18n()
const session = useExamSessionStore()

const needRefresh = ref(false)
const queued = ref(false)
let updateSW: ((reloadPage?: boolean) => Promise<void>) | undefined

onMounted(async () => {
  try {
    const { registerSW } = await import('virtual:pwa-register')
    updateSW = registerSW({
      immediate: true,
      onNeedRefresh() {
        if (session.isInProgress) {
          queued.value = true
        } else {
          needRefresh.value = true
        }
      },
    })
  } catch {
    /* PWA not available in dev */
  }
})

watch(
  () => session.isInProgress,
  (inProgress) => {
    if (!inProgress && queued.value) {
      queued.value = false
      needRefresh.value = true
    }
  },
)

function applyUpdate() {
  updateSW?.(true)
}

function dismissUpdate() {
  needRefresh.value = false
}
</script>

<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="needRefresh"
        class="update-toast fixed bottom-20 left-4 right-4 z-50 mx-auto max-w-md rounded-xl border border-border bg-surface-raised p-4 shadow-lg"
      >
        <p class="mb-3 text-sm font-medium text-on-surface">{{ t('update.available') }}</p>
        <div class="flex gap-2">
          <button
            class="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-dark"
            @click="applyUpdate"
          >
            {{ t('update.refresh') }}
          </button>
          <button
            class="rounded-lg px-4 py-2 text-sm font-medium text-on-surface-muted transition hover:bg-surface-alt"
            @click="dismissUpdate"
          >
            {{ t('update.later') }}
          </button>
        </div>
      </div>
    </Transition>
    <p
      v-if="queued && !needRefresh"
      class="fixed bottom-20 left-4 right-4 z-50 mx-auto max-w-md rounded-xl border border-border bg-surface-raised px-4 py-3 text-center text-xs text-on-surface-muted shadow-lg"
    >
      {{ t('update.deferred') }}
    </p>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
