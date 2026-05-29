<template>
  <div class="max-w-7xl mx-auto space-y-8">
    <div class="text-center mb-10 pt-4">
      <h1 class="text-3xl font-bold mb-3">
        <span class="gradient-text">{{ t('homeTitle') }}</span>
        <span class="text-gray-400 font-normal text-xl ml-2">{{ t('homeSubtitle') }}</span>
      </h1>
      <p class="text-gray-500 text-sm max-w-lg mx-auto">
        {{ t('homeDesc') }}
      </p>

      <div v-if="authStore.isLoggedIn" class="mt-4 inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-white/[0.03] border border-white/5">
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">{{ locale === 'zh' ? '今日下载' : 'Today' }}</span>
          <span v-if="isUnlimited" class="text-sm font-bold text-purple-400">∞ 无限</span>
          <span v-else class="text-sm font-bold" :class="dailyRemaining === 0 ? 'text-red-400' : dailyRemaining <= 2 ? 'text-yellow-400' : 'text-emerald-400'">
            {{ dailyUsed }}/{{ dailyLimit }}
          </span>
        </div>
        <span v-if="!isUnlimited" class="text-xs" :class="dailyRemaining === 0 ? 'text-red-400' : 'text-gray-500'">
          {{ dailyRemaining === 0 ? '次数已用完' : '剩余 ' + dailyRemaining + ' 次' }}
        </span>
        <span v-if="!isUnlimited && resetHint" class="text-xs text-gray-600" :title="resetsAt">
          {{ resetHint }}
        </span>
        <router-link
          v-if="dailyRemaining <= 2 && membershipStore.currentPlan !== 'pro'"
          to="/pricing"
          class="px-3 py-1 rounded-lg text-xs font-medium bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] text-white hover:opacity-90 transition-opacity"
        >
          升级会员
        </router-link>
      </div>
    </div>

    <UrlInput />

    <!-- Video Preview with AI Features (New Layout) -->
    <VideoPreview />

    <section v-if="store.tasks.length > 0" class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h2 class="text-base font-bold text-gray-200 flex items-center gap-2">
            <svg class="w-5 h-5 text-[#6C63FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
            </svg>
            {{ t('downloadQueue') }}
            <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-[#6C63FF]/15 text-[#6C63FF]">{{ store.tasks.length }}</span>
          </h2>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <span>{{ store.activeTasks.length }} {{ t('active') }}</span>
          <span class="text-gray-700">|</span>
          <span>{{ store.completedTasks.length }} {{ t('done') }}</span>
        </div>
      </div>

      <div class="grid gap-3 md:grid-cols-2">
        <DownloadCard
          v-for="task in sortedTasks"
          :key="task.id"
          :task="task"
          @pause="handlePause"
          @resume="handleResume"
          @cancel="handleCancel"
          @retry="handleRetry"
        />
      </div>
    </section>

    <section v-if="!store.tasks.length && !store.parseResult" class="py-20 text-center">
      <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white/[0.02] border border-white/5 mb-6">
        <svg class="w-10 h-10 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
        </svg>
      </div>
      <h3 class="text-lg font-semibold text-gray-400 mb-2">{{ locale === 'zh' ? '暂无下载任务' : 'No downloads yet' }}</h3>
      <p class="text-sm text-gray-600 max-w-sm mx-auto">{{ locale === 'zh' ? '在上方粘贴视频链接开始下载，支持所有主流视频平台。' : 'Paste a video link above to get started. We support all major video platforms.' }}</p>

      <div class="mt-8 flex items-center justify-center gap-4 flex-wrap">
        <span
          v-for="platform in supportedPlatforms"
          :key="platform.name"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-default hover:bg-white/5"
          :class="platform.class"
        >
          {{ platform.name }}
        </span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useDownloadStore } from '../stores/download'
import { useAuthStore } from '../stores/auth'
import { useMembershipStore } from '../stores/membership'
import { useI18n } from '../composables/useI18n'
import UrlInput from '../components/download/UrlInput.vue'
import VideoPreview from '../components/download/VideoPreview.vue'
import DownloadCard from '../components/download/DownloadCard.vue'

const store = useDownloadStore()
const authStore = useAuthStore()
const membershipStore = useMembershipStore()
const { t, locale } = useI18n()

const dailyUsed = ref(0)
const dailyLimit = ref(5)
const dailyRemaining = ref(5)
const isUnlimited = ref(false)
const resetsAt = ref('')
const resetHint = ref('')

function formatResetHint(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return locale.value === 'zh' ? '每日 0 点重置' : 'Resets at midnight'
  const h = d.getHours().toString().padStart(2, '0')
  const m = d.getMinutes().toString().padStart(2, '0')
  return locale.value === 'zh' ? `每日 ${h}:${m} 重置` : `Resets daily ${h}:${m}`
}

onMounted(() => {
  fetchUsage()
})

async function fetchUsage() {
  if (!authStore.token) return
  try {
    const res = await fetch('/api/membership/usage', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    const data = await res.json()
    if (data.success && data.data) {
      dailyUsed.value = data.data.downloads.used
      dailyLimit.value = data.data.downloads.limit
      dailyRemaining.value = data.data.downloads.remaining
      isUnlimited.value = data.data.is_unlimited
      resetsAt.value = data.data.resets_at || ''
      resetHint.value = formatResetHint(resetsAt.value)
    }
  } catch (e) {
    console.warn('Failed to fetch usage:', e)
  }
}

const sortedTasks = computed(() =>
  [...store.tasks].sort((a, b) => b.created_at - a.created_at)
)

const supportedPlatforms = [
  { name: 'YouTube', class: 'text-red-400' },
  { name: 'Bilibili', class: 'text-pink-400' },
  { name: 'TikTok', class: 'text-white/40' },
  { name: 'Instagram', class: 'text-fuchsia-400' },
  { name: 'Twitter/X', class: 'text-blue-400' },
  { name: 'Douyin', class: 'text-cyan-400' },
]

async function handlePause(id) {
  await store.pauseTask(id)
}

async function handleResume(id) {
  await store.resumeTask(id)
}

async function handleCancel(id) {
  await store.cancelTask(id)
}

async function handleRetry(task) {
  const result = await store.startDownload({
    url: task.url,
    format_id: task.format_id,
    output_format: task.output_format,
  })
  if (result && result.error) {
    alert(result.error)
  }
  fetchUsage()
}
</script>
