<template>
  <div class="group relative rounded-xl border transition-all duration-300 card-hover"
    :class="statusBorderClass">
    <div class="p-4 space-y-3">
      <div class="flex items-start gap-3">
        <div class="w-14 h-10 rounded-lg overflow-hidden shrink-0 bg-black/40 ring-1 ring-white/5">
          <img
            v-if="task.thumbnail"
            :src="proxyUrl(task.thumbnail)"
            :alt="task.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
          </div>
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md" :class="statusBadgeClass">
              {{ statusLabel }}
            </span>
            <span class="text-[10px] text-gray-600 truncate">{{ task.id }}</span>
          </div>
          <h4 class="text-sm font-semibold text-gray-200 truncate">{{ task.title || t('loading') }}</h4>
          <p class="text-xs text-gray-500 truncate mt-0.5">{{ task.platform || '' }} · {{ task.format_id || 'auto' }}</p>
        </div>
      </div>

      <div v-if="isProgressStatus" class="space-y-2">
        <div class="relative h-2 rounded-full bg-white/5 overflow-hidden">
          <div
            class="absolute inset-y-0 left-0 rounded-full progress-bar-animated transition-all duration-300"
            :style="{ width: `${Math.min(task.progress, 100)}%` }"
          ></div>
        </div>
        <div class="flex items-center justify-between text-[11px]">
          <div class="flex items-center gap-3">
            <span class="font-mono font-bold text-[#6C63FF]">{{ task.progress.toFixed(1) }}%</span>
            <span v-if="task.speed" class="text-emerald-400 font-mono">{{ task.speed }}</span>
          </div>
          <span v-if="task.eta" class="text-gray-500 font-mono">{{ task.eta }}</span>
        </div>
      </div>

      <div v-if="task.status === 'completed'" class="flex items-center gap-2 text-xs">
        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <span class="text-emerald-400 font-medium">Completed</span>
        <span v-if="task.filesize" class="text-gray-500 ml-auto">{{ formatSize(task.filesize) }}</span>
      </div>

      <div v-if="task.status === 'failed'" class="rounded-lg bg-red-500/5 border border-red-500/10 p-2">
        <p class="text-xs text-red-400 line-clamp-2">{{ task.error_message || 'Unknown error' }}</p>
      </div>

      <div class="flex items-center gap-2 pt-1">
        <template v-if="task.status === 'downloading' || task.status === 'queued' || task.status === 'merging'">
          <button
            v-if="task.status === 'downloading'"
            @click="$emit('pause', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-yellow-500/10 text-yellow-400 text-xs font-medium hover:bg-yellow-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6"/></svg>
            {{ t('pause') }}
          </button>
          <button
            v-if="task.status === 'paused'"
            @click="$emit('resume', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            Resume
          </button>
          <button
            @click="$emit('cancel', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-red-500/10 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            {{ t('cancel') }}
          </button>
        </template>

        <template v-if="task.status === 'paused'">
          <button
            @click="$emit('resume', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            {{ t('resume') }}
          </button>
          <button
            @click="$emit('cancel', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-red-500/10 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            {{ t('remove') }}
          </button>
        </template>

        <template v-if="task.status === 'completed'">
          <button
            @click="openFile"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-[#6C63FF]/10 text-[#6C63FF] text-xs font-medium hover:bg-[#6C63FF]/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            {{ t('openFile') }}
          </button>
          <button
            @click="$emit('cancel', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-white/5 text-gray-400 text-xs font-medium hover:bg-white/10 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            {{ t('remove') }}
          </button>
        </template>

        <template v-if="task.status === 'failed'">
          <button
            @click="$emit('retry', task)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-[#6C63FF]/10 text-[#6C63FF] text-xs font-medium hover:bg-[#6C63FF]/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            {{ t('retry') }}
          </button>
          <button
            @click="$emit('cancel', task.id)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-red-500/10 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors"
          >
            Remove
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../../composables/useI18n'

const { t, locale } = useI18n()

const props = defineProps({
  task: { type: Object, required: true },
})

defineEmits(['pause', 'resume', 'cancel', 'retry'])

function proxyUrl(url) {
  if (!url) return ''
  if (url.startsWith('/api') || url.startsWith('data:')) return url
  return `/api/proxy-image?url=${encodeURIComponent(url)}`
}

const isProgressStatus = computed(() => ['queued', 'downloading', 'merging'].includes(props.task.status))

const statusMap = computed(() => ({
  queued: { label: t.value('queued'), badge: 'bg-gray-500/10 text-gray-400 border: border-gray-500/10' },
  downloading: { label: t.value('downloading'), badge: 'bg-blue-500/10 text-blue-400 border: border-blue-500/20' },
  paused: { label: t.value('paused'), badge: 'bg-yellow-500/10 text-yellow-400 border: border-yellow-500/20' },
  merging: { label: t.value('processing'), badge: 'bg-purple-500/10 text-purple-400 border: border-purple-500/20' },
  completed: { label: t.value('completed'), badge: 'bg-emerald-500/10 text-emerald-400 border: border-emerald-500/20' },
  failed: { label: t.value('failed'), badge: 'bg-red-500/10 text-red-400 border: border-red-500/20' },
}))

const statusInfo = computed(() => statusMap.value[props.task.status] || statusMap.value.queued)
const statusLabel = statusInfo.value.label
const statusBadgeClass = statusInfo.value.badge

const statusBorderClass = computed(() => {
  const map = {
    queued: 'border-white/5',
    downloading: 'border-blue-500/20',
    paused: 'border-yellow-500/20',
    merging: 'border-purple-500/20',
    completed: 'border-emerald-500/20',
    failed: 'border-red-500/20',
  }
  return map[props.task.status] || 'border-white/5'
})

function formatSize(bytes) {
  if (!bytes) return '--'
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

async function openFile() {
  try {
    const res = await fetch(`/api/download/${props.task.id}/open`)
    const data = await res.json()
    if (!data.ok) {
      alert(data.detail || 'Cannot open file')
    }
  } catch (e) {
    alert('Open file failed: ' + e.message)
  }
}
</script>
