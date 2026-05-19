<template>
  <div v-if="formats.length" class="space-y-2">
    <div class="flex items-center justify-between mb-2">
      <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('selectFormat') }}</label>
      <span class="text-xs text-[#6C63FF] font-medium cursor-pointer hover:underline" @click="showAll = !showAll">
        {{ showAll ? t('showLess') : `${t('showAll')} (${formats.length})` }}
      </span>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
      <button
        v-for="(fmt, idx) in displayFormats"
        :key="fmt.format_id"
        @click="selectFormat(fmt)"
        :class="[
          'group relative px-3 py-2.5 rounded-xl text-left transition-all duration-200 border',
          selected?.format_id === fmt.format_id
            ? 'border-[#6C63FF]/50 bg-[#6C63FF]/10 shadow-lg shadow-purple-500/10'
            : 'border-white/5 bg-white/[0.02] hover:bg-white/5 hover:border-white/10'
        ]"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold" :class="selected?.format_id === fmt.format_id ? 'text-[#6C63FF]' : 'text-gray-300'">
            {{ fmt.resolution || 'N/A' }}
          </span>
          <span class="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/5 text-gray-500">{{ fmt.ext }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-[11px] text-gray-500">{{ formatSize(fmt.filesize) }}</span>
          <span v-if="fmt.tbr" class="text-[10px] text-gray-600">{{ fmt.tbr }}kbps</span>
        </div>

        <div v-if="selected?.format_id === fmt.format_id" class="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-[#6C63FF] flex items-center justify-center">
          <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
      </button>
    </div>

    <div v-if="store.parseResult.best_format" class="mt-3 px-3 py-2 rounded-lg bg-gradient-to-r from-[#6C63FF]/5 to-[#3B82F6]/5 border border-[#6C63FF]/10 flex items-center gap-2">
      <svg class="w-4 h-4 text-[#6C63FF] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
      </svg>
      <span class="text-xs text-gray-400">
        {{ t('recommended') }}: <span class="font-semibold text-[#6C63FF]">{{ store.parseResult.best_format.resolution }} {{ store.parseResult.best_format.ext }}</span>
        <span class="text-gray-500 ml-1">{{ store.parseResult.best_format.note }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDownloadStore } from '../../stores/download'
import { useI18n } from '../../composables/useI18n'

const store = useDownloadStore()
const { t, locale } = useI18n()
const selected = ref(null)
const showAll = ref(false)

const formats = computed(() => store.parseResult?.formats || [])

const displayFormats = computed(() => {
  const sorted = [...formats.value].sort((a, b) => {
    const aScore = a.vcodec !== 'none' && a.acodec !== 'none' ? 100 : a.vcodec !== 'none' ? 50 : 0
    const bScore = b.vcodec !== 'none' && b.acodec !== 'none' ? 100 : b.vcodec !== 'none' ? 50 : 0
    return bScore - aScore
  })
  return showAll.value ? sorted.slice(0, 15) : sorted.slice(0, 6)
})

function selectFormat(fmt) {
  selected.value = selected.value?.format_id === fmt.format_id ? null : fmt
}

function formatSize(bytes) {
  if (!bytes) return '--'
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`
}
</script>
