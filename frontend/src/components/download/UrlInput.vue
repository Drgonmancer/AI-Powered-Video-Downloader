<template>
  <div class="relative group">
    <div class="absolute -inset-0.5 bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] rounded-2xl opacity-20 group-hover:opacity-40 blur transition-opacity duration-500"></div>
    <div class="relative bg-[#1A1A2E] rounded-2xl p-1">
      <form @submit.prevent="handleSubmit" class="flex items-center gap-2">
        <div class="flex-1 flex items-center gap-3 px-5 py-4">
          <svg class="w-5 h-5 text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
          </svg>
          <input
            ref="inputRef"
            v-model="url"
            type="text"
            :placeholder="locale === 'zh' ? '粘贴视频链接... 支持 YouTube、B站、抖音、TikTok 等' : 'Paste video URL here... YouTube, Bilibili, TikTok, Instagram & more'"
            class="flex-1 bg-transparent text-gray-200 placeholder-gray-600 text-sm outline-none min-w-0"
            :disabled="store.isParsing"
          />
        </div>

        <button
          type="submit"
          :disabled="!url.trim() || store.isParsing"
          :class="[
            'm-1 px-7 py-4 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center gap-2',
            url.trim() && !store.isParsing
              ? 'bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02]'
              : 'bg-gray-700/30 text-gray-500 cursor-not-allowed'
          ]"
        >
          <svg v-if="!store.isParsing" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ store.isParsing ? t('parsing') : t('parseBtn') }}
        </button>
      </form>
    </div>

    <div v-if="store.parseError" class="mt-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3">
      <svg class="w-5 h-5 text-red-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span class="text-sm text-red-300">{{ store.parseError }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDownloadStore } from '../../stores/download'
import { useI18n } from '../../composables/useI18n'

const store = useDownloadStore()
const { t, locale } = useI18n()
const url = ref('')
const inputRef = ref(null)

async function handleSubmit() {
  if (!url.value.trim() || store.isParsing) return
  await store.parseUrl(url.value.trim())
}
</script>
