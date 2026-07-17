<script setup lang="ts">
import { watch } from 'vue'
import { RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/AppHeader.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import UpdateToast from '@/components/UpdateToast.vue'
import InstallHint from '@/components/InstallHint.vue'

const { locale } = useI18n()

watch(
  locale,
  (value) => {
    document.documentElement.lang = value === 'zh-TW' ? 'zh-Hant' : 'en'
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <AppHeader />
    <main id="main-content" class="flex-1" role="main">
      <RouterView />
    </main>
    <AppBottomNav />
    <UpdateToast />
    <InstallHint />
  </div>
</template>
