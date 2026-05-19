<template>
  <header class="h-16 border-b border-white/5 flex items-center justify-between px-6 shrink-0 bg-[#0F0F1A]/80 backdrop-blur-sm">
    <div class="flex items-center gap-4">
      <h2 class="text-base font-semibold text-gray-300">{{ title }}</h2>
      <span v-if="subtitle" class="text-xs text-gray-500">{{ subtitle }}</span>
    </div>

    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/5">
        <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
        <span class="text-xs text-gray-400">{{ t('serverOnline') }}</span>
      </div>

      <button
        @click="$router.push('/settings')"
        class="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '../../composables/useI18n'

const route = useRoute()
const { t, locale } = useI18n()

const titles = computed(() => ({
  '/': { title: locale.value === 'zh' ? '控制台' : 'Dashboard', subtitle: locale.value === 'zh' ? '下载和管理视频' : 'Download & manage videos' },
  '/settings': { title: t.value('settings'), subtitle: t.value('settingsDesc') },
}))

const current = computed(() => titles.value[route.path] || { title: '', subtitle: '' })
const title = current.value.title
const subtitle = current.value.subtitle
</script>
