<template>
  <transition name="slide-up" appear>
    <div v-if="store.parseResult" class="animate-pulse-glow">
      <div class="relative rounded-2xl overflow-hidden border border-white/5 bg-[#1A1A2E]">
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#6C63FF]/50 to-transparent"></div>

        <div class="flex flex-col md:flex-row gap-6 p-6">
          <div class="shrink-0 relative group/thumb">
            <div class="w-full md:w-72 aspect-video rounded-xl overflow-hidden bg-black/50 ring-1 ring-white/10">
              <img
                v-if="store.parseResult.thumbnail"
                :src="proxyUrl(store.parseResult.thumbnail)"
                :alt="store.parseResult.title"
                class="w-full h-full object-cover transition-transform duration-500 group-hover/thumb:scale-105"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-16 h-16 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
              </div>
            </div>
            <div v-if="store.parseResult.duration" class="absolute bottom-2 right-2 px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-sm text-xs font-mono text-white">
              {{ formatDuration(store.parseResult.duration) }}
            </div>
          </div>

          <div class="flex-1 min-w-0 space-y-4">
            <div>
              <div class="flex items-start justify-between gap-3 mb-1">
                <h3 class="text-lg font-bold text-gray-100 leading-tight line-clamp-2">{{ store.parseResult.title }}</h3>
                <span class="shrink-0 px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider"
                  :class="platformColor(store.parseResult.platform)">
                  {{ store.parseResult.platform }}
                </span>
              </div>
              <p v-if="store.parseResult.uploader" class="text-sm text-gray-500 mt-1">by {{ store.parseResult.uploader }}</p>
            </div>

            <FormatSelector />

            <div class="flex flex-wrap gap-3 pt-2">
              <button
                @click="handleDownload('best')"
                :disabled="store.isSubmittingDownload"
                class="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] text-white font-semibold text-sm hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300 hover:scale-[1.02] disabled:opacity-60 disabled:cursor-wait disabled:hover:scale-100"
              >
                <svg v-if="store.isSubmittingDownload" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                {{ store.isSubmittingDownload ? (locale === 'zh' ? '提交中…' : 'Submitting…') : t('downloadBest') }}
              </button>

              <button
                @click="handleDownload('audio')"
                :disabled="store.isSubmittingDownload"
                class="flex items-center gap-2 px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 font-medium text-sm hover:bg-white/10 hover:border-[#6C63FF]/30 transition-all duration-300 disabled:opacity-60 disabled:cursor-wait"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                </svg>
                {{ t('extractAudio') }}
              </button>

              <button
                v-if="store.parseResult.is_playlist || store.parseResult.entry_count > 1"
                @click="handleBatchDownload"
                class="flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-medium text-sm hover:bg-emerald-500/20 transition-all duration-300"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
                {{ t('batchDownload') }} ({{ store.parseResult.playlist_count || store.parseResult.entry_count }})
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useDownloadStore } from '../../stores/download'
import { useI18n } from '../../composables/useI18n'
import FormatSelector from './FormatSelector.vue'

function proxyUrl(url) {
  if (!url) return ''
  if (url.startsWith('/api') || url.startsWith('data:')) return url
  return `/api/proxy-image?url=${encodeURIComponent(url)}`
}

const store = useDownloadStore()
const { t, locale } = useI18n()

function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

function platformColor(platform) {
  const colors = {
    youtube: 'bg-red-500/15 text-red-400',
    bilibili: 'bg-pink-500/15 text-pink-400',
    douyin: 'bg-cyan-500/15 text-cyan-400',
    kuaishou: 'bg-orange-500/15 text-orange-400',
    twitter: 'bg-blue-500/15 text-blue-400',
    instagram: 'bg-fuchsia-500/15 text-fuchsia-400',
    tiktok: 'bg-gray-500/15 text-gray-400',
  }
  return colors[platform] || 'bg-gray-500/15 text-gray-400'
}

async function handleDownload(mode) {
  let formatId = ''
  if (mode === 'best' && store.parseResult.best_format) {
    formatId = store.parseResult.best_format.format_id
  } else if (mode === 'audio') {
    const audioFormats = (store.parseResult.formats || []).filter(f => f.vcodec === 'none')
    if (audioFormats.length) {
      const bestAudio = audioFormats.reduce((a, b) => (b.tbr || 0) > (a.tbr || 0) ? b : a)
      formatId = bestAudio.format_id
    }
  }
  const result = await store.startDownload({
    url: store.parseResult.entries?.[0] || store.lastParsedUrl || '',
    format_id: formatId,
    output_format: mode === 'audio' ? 'mp3' : store.settings.output_format || 'mp4',
    title: store.parseResult.title || '',
    thumbnail: store.parseResult.thumbnail || '',
    platform: store.parseResult.platform || '',
    duration: store.parseResult.duration || 0,
    _direct_url: store.parseResult._direct_url || '',
  })
  if (result?.error) {
    alert(result.error)
  }
}

async function handleBatchDownload() {
  if (store.parseResult.entries?.length) {
    await store.batchDownload(null, {
      urls: store.parseResult.entries,
      output_format: store.settings.output_format || 'mp4',
    })
  } else {
    await store.batchDownload(store.parseResult.url || store.lastParsedUrl || '', {
      output_format: store.settings.output_format || 'mp4',
    })
  }
}
</script>

<style scoped>
.slide-up-enter-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
