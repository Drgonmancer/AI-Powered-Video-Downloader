<template>
  <aside class="w-64 bg-[#12122a] border-r border-white/5 flex flex-col shrink-0">
    <div class="p-6 border-b border-white/5">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#6C63FF] to-[#3B82F6] flex items-center justify-center shadow-lg shadow-purple-500/20">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold gradient-text">{{ t('appTitle') }}</h1>
          <span class="text-[10px] text-gray-500 font-medium tracking-wider uppercase">{{ locale === 'zh' ? '专业版' : 'Pro Edition' }}</span>
        </div>
      </div>
    </div>

    <nav class="flex-1 py-4 px-3 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.path + item.label"
        :to="item.path"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
          isActive(item.path)
            ? 'bg-gradient-to-r from-[#6C63FF]/20 to-[#3B82F6]/10 text-white shadow-lg shadow-purple-500/5 border border-[#6C63FF]/20'
            : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
        ]"
      >
        <component :is="item.icon" class="w-5 h-5 shrink-0" />
        <span>{{ item.label }}</span>
        <span
          v-if="item.badge !== undefined"
          :class="[
            'ml-auto text-xs px-2 py-0.5 rounded-full font-semibold',
            item.badge > 0 ? 'bg-[#6C63FF] text-white' : 'bg-gray-700/50 text-gray-500'
          ]"
        >{{ item.badge || 0 }}</span>
      </router-link>
    </nav>

    <div class="p-4 m-3 rounded-xl bg-gradient-to-br from-[#6C63FF]/10 to-[#3B82F6]/5 border border-[#6C63FF]/10">
      <div class="flex items-center gap-2 mb-2">
        <div
          class="w-2 h-2 rounded-full"
          :class="[
            store.wsStatus === 'connected' ? 'bg-emerald-400' :
            store.wsStatus === 'failed' ? 'bg-gray-500' : 'bg-amber-400 animate-pulse'
          ]"
        ></div>
        <span
          class="text-xs font-medium"
          :class="[
            store.wsStatus === 'connected' ? 'text-emerald-400' :
            store.wsStatus === 'failed' ? 'text-gray-400' : 'text-amber-400'
          ]"
        >
          {{ wsLabel }}
        </span>
        <button
          v-if="store.wsStatus === 'failed'"
          type="button"
          class="ml-auto text-[10px] text-[#6C63FF] hover:underline"
          @click="store.reconnect()"
        >
          {{ locale === 'zh' ? '重试' : 'Retry' }}
        </button>
      </div>
      <p class="text-[11px] text-gray-500">{{ t('wsStatusHint') }}</p>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed, h } from 'vue'
import { useDownloadStore } from '../../stores/download'
import { useI18n } from '../../composables/useI18n'

const store = useDownloadStore()
const route = useRoute()
const { t, locale } = useI18n()

const wsLabel = computed(() => {
  const key = {
    connected: 'wsConnected',
    connecting: 'wsConnecting',
    reconnecting: 'wsReconnecting',
    failed: 'wsFailed',
    idle: 'wsDisconnected',
  }[store.wsStatus] || 'wsDisconnected'
  return t.value(key)
})

const isActive = (path) => route.path === path

function HomeIcon() {
  return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
  ])
}

function DownloadIcon() {
  return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10' })
  ])
}

function SettingsIcon() {
  return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }),
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' })
  ])
}

const navItems = computed(() => [
  { path: '/', label: locale.value === 'zh' ? '首页' : 'Home', icon: HomeIcon },
  {
    path: '/',
    label: locale.value === 'zh' ? '下载任务' : 'Downloads',
    icon: DownloadIcon,
    badge: store.activeTasks.length,
  },
  { path: '/settings', label: t.value('settings'), icon: SettingsIcon },
])
</script>
