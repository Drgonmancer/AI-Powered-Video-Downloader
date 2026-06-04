<template>
  <div class="flex h-screen overflow-hidden">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-y-auto p-6">
        <router-view v-slot="{ Component, route }">
          <component :is="Component" v-if="Component" :key="route.fullPath" />
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useDownloadStore } from '../../stores/download'
import { useUsageRealtime } from '../../composables/useUsageRealtime'

const downloadStore = useDownloadStore()
useUsageRealtime()

onMounted(() => {
  downloadStore.init()
})
</script>

