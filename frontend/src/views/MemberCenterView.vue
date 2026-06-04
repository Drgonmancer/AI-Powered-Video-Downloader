<template>
  <div class="max-w-3xl mx-auto py-8 px-4 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">
        <span class="gradient-text">个人中心</span>
      </h1>
      <span
        class="px-3 py-1 rounded-full text-xs font-semibold border"
        :class="badgeClass"
      >
        {{ authStore.roleLabel }}
      </span>
    </div>

    <p v-if="loading" class="text-gray-500 text-sm text-center py-4">加载中...</p>

    <!-- 个人资料 -->
    <section class="rounded-2xl border border-white/10 bg-[#1A1A2E] p-6 space-y-5">
      <h2 class="text-sm font-bold text-gray-300 uppercase tracking-wider">个人资料</h2>
      <div class="flex items-center gap-5">
        <div class="relative group">
          <img
            v-if="authStore.userAvatar"
            :src="authStore.userAvatar"
            alt="avatar"
            class="w-20 h-20 rounded-full object-cover ring-2 ring-[#6C63FF]/50"
          />
          <div
            v-else
            class="w-20 h-20 rounded-full bg-gradient-to-br from-[#6C63FF] to-purple-600 flex items-center justify-center text-white text-2xl font-bold"
          >
            {{ authStore.userName?.charAt(0)?.toUpperCase() || '?' }}
          </div>
          <label
            class="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity"
          >
            <span class="text-white text-xs">更换</span>
            <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          </label>
        </div>
        <div class="flex-1 min-w-0 space-y-1">
          <p class="text-white font-semibold truncate">{{ authStore.userName || '未设置昵称' }}</p>
          <p class="text-gray-500 text-sm truncate">{{ authStore.userEmail }}</p>
          <label class="inline-block mt-1 cursor-pointer text-xs text-[#6C63FF] hover:underline">
            上传头像
            <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          </label>
        </div>
      </div>

      <div>
        <label class="text-gray-400 text-xs mb-1.5 block">昵称</label>
        <div class="flex gap-2">
          <input
            v-model="usernameInput"
            type="text"
            maxlength="50"
            placeholder="设置你的昵称"
            class="flex-1 px-4 py-2.5 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50"
          />
          <button
            class="px-5 py-2.5 rounded-xl text-sm font-medium text-white bg-[#6C63FF] hover:bg-[#5a52e0] disabled:opacity-50"
            :disabled="savingUsername"
            @click="saveUsername"
          >
            {{ savingUsername ? '保存中' : '保存' }}
          </button>
        </div>
      </div>
      <p v-if="profileError" class="text-red-400 text-xs">{{ profileError }}</p>
    </section>

    <!-- 身份与会员 -->
    <section class="rounded-2xl border border-white/10 bg-[#1A1A2E] p-6 space-y-4">
      <h2 class="text-sm font-bold text-gray-300 uppercase tracking-wider">身份与会员</h2>

      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-xl bg-black/20 p-4 border border-white/5">
          <p class="text-gray-500 text-xs mb-1">账户类型</p>
          <p class="text-white font-semibold">{{ authStore.roleLabel }}</p>
        </div>
        <div class="rounded-xl bg-black/20 p-4 border border-white/5">
          <p class="text-gray-500 text-xs mb-1">当前套餐</p>
          <p class="text-white font-semibold">{{ authStore.planName }}</p>
        </div>
      </div>

      <template v-if="authStore.isVip || membershipStore.currentPeriodEnd">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div class="flex items-center justify-between sm:block">
            <span class="text-gray-400 text-sm">VIP 开通时间</span>
            <span class="text-gray-200 text-sm sm:mt-1 sm:block">{{ formatDate(periodStart) }}</span>
          </div>
          <div class="flex items-center justify-between sm:block">
            <span class="text-gray-400 text-sm">VIP 到期时间</span>
            <span class="text-gray-200 text-sm sm:mt-1 sm:block">{{ formatDate(periodEnd) }}</span>
          </div>
        </div>
        <p
          v-if="membershipStore.membershipTimeRemaining"
          class="text-amber-400/90 text-xs"
        >
          剩余：{{ membershipStore.membershipTimeRemaining }}
        </p>
      </template>
      <p v-else class="text-gray-500 text-sm">
        升级 VIP 后可查看会员周期起止时间
      </p>

      <div v-if="membershipStore.cancelAtPeriodEnd" class="text-yellow-400 text-xs bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-3 py-2">
        已申请取消订阅，将在当前周期结束后失效
      </div>

      <div class="flex gap-3 pt-1">
        <router-link
          to="/pricing"
          class="flex-1 text-center py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#6C63FF] to-[#3B82F6]"
        >
          {{ authStore.isVip ? '管理套餐' : '升级 VIP' }}
        </router-link>
        <button
          v-if="canCancel"
          class="flex-1 py-2.5 rounded-xl text-sm font-medium text-red-400 border border-red-500/30 hover:bg-red-500/10 disabled:opacity-50"
          :disabled="canceling"
          @click="handleCancel"
        >
          {{ canceling ? '处理中...' : '取消订阅' }}
        </button>
      </div>
      <p v-if="membershipError" class="text-red-400 text-xs">{{ membershipError }}</p>
    </section>

    <!-- 权限与用量 -->
    <section class="rounded-2xl border border-white/10 bg-[#1A1A2E] p-6 space-y-5">
      <h2 class="text-sm font-bold text-gray-300 uppercase tracking-wider">今日权限用量</h2>
      <p v-if="usageResetsAt" class="text-gray-500 text-xs -mt-2">
        统计日 {{ usageDate }} · 将于 {{ formatDate(usageResetsAt) }} 重置（{{ resetTimezone }}）
      </p>

      <!-- 下载次数 -->
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="text-gray-400">视频下载</span>
          <span class="text-gray-200">
            <template v-if="downloadsUnlimited">已用 {{ downloadsUsed }} 次 · 不限量</template>
            <template v-else>已用 {{ downloadsUsed }} / {{ downloadsLimit }} 次 · 剩余 {{ downloadsRemaining }}</template>
          </span>
        </div>
        <div class="h-2 rounded-full bg-black/40 overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="downloadsUnlimited ? 'bg-gradient-to-r from-purple-500 to-pink-500 w-full' : 'bg-gradient-to-r from-[#6C63FF] to-[#3B82F6]'"
            :style="downloadsUnlimited ? {} : { width: downloadProgress + '%' }"
          />
        </div>
      </div>

      <!-- AI 摘要额度 -->
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="text-gray-400">AI 视频摘要</span>
          <span class="text-gray-200">
            <template v-if="aiUnlimited">套餐额度：不限量</template>
            <template v-else>套餐每日额度：{{ aiLimit }} 次</template>
          </span>
        </div>
        <p class="text-gray-600 text-xs">按当前套餐展示额度；下载次数每日零点重置</p>
      </div>

      <!-- 画质等权益 -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
        <div class="rounded-lg bg-black/20 px-3 py-2 border border-white/5 text-center">
          <p class="text-gray-500 text-xs">最高画质</p>
          <p class="text-white text-sm font-medium mt-0.5">{{ maxQuality }}</p>
        </div>
        <div class="rounded-lg bg-black/20 px-3 py-2 border border-white/5 text-center">
          <p class="text-gray-500 text-xs">批量下载</p>
          <p class="text-white text-sm font-medium mt-0.5">{{ batchDownload ? '支持' : '不支持' }}</p>
        </div>
        <div class="rounded-lg bg-black/20 px-3 py-2 border border-white/5 text-center col-span-2 sm:col-span-1">
          <p class="text-gray-500 text-xs">今日已下载</p>
          <p class="text-white text-sm font-medium mt-0.5">{{ downloadsUsed }} 次</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useMembershipStore } from '../stores/membership'

const authStore = useAuthStore()
const membershipStore = useMembershipStore()

const usernameInput = ref('')
const savingUsername = ref(false)
const canceling = ref(false)
const loading = ref(false)
const profileError = ref('')
const membershipError = ref('')

const badgeClass = computed(() => {
  const label = authStore.roleLabel
  if (label === '管理员') return 'bg-amber-500/15 text-amber-300 border-amber-500/30'
  if (label === 'PRO会员') return 'bg-purple-500/15 text-purple-300 border-purple-500/30'
  if (label === 'VIP会员') return 'bg-blue-500/15 text-blue-300 border-blue-500/30'
  return 'bg-gray-500/15 text-gray-300 border-gray-500/30'
})

const periodStart = computed(() =>
  authStore.membership?.current_period_start || membershipStore.currentPeriodStart
)
const periodEnd = computed(() =>
  authStore.membership?.current_period_end || membershipStore.currentPeriodEnd
)

const usageData = computed(() => authStore.usage || {})
const downloadsUsed = computed(() => usageData.value.downloads?.used ?? 0)
const downloadsLimit = computed(() => usageData.value.downloads?.limit ?? 5)
const downloadsRemaining = computed(() => usageData.value.downloads?.remaining ?? 0)
const downloadsUnlimited = computed(() => !!usageData.value.downloads?.is_unlimited)
const downloadProgress = computed(() => {
  if (downloadsUnlimited.value) return 100
  const limit = downloadsLimit.value
  if (!limit || limit <= 0) return 0
  return Math.min(100, Math.round((downloadsUsed.value / limit) * 100))
})

const aiLimit = computed(() => usageData.value.ai_summaries?.limit ?? 3)
const aiUnlimited = computed(() => aiLimit.value === -1)
const usageDate = computed(() => usageData.value.usage_date || '—')
const usageResetsAt = computed(() => usageData.value.resets_at || '')
const resetTimezone = computed(() => usageData.value.reset_timezone || 'UTC')

const features = computed(() => authStore.membership?.features || {})
const maxQuality = computed(() => features.value.max_quality || '720p')
const batchDownload = computed(() => !!features.value.batch_download)

const canCancel = computed(() =>
  membershipStore.isActive &&
  membershipStore.currentPlan !== 'free' &&
  !membershipStore.cancelAtPeriodEnd
)

function formatDate(str) {
  if (!str) return '—'
  try {
    const d = new Date(String(str).replace(' ', 'T'))
    if (Number.isNaN(d.getTime())) return str
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return str
  }
}

async function saveUsername() {
  profileError.value = ''
  savingUsername.value = true
  try {
    await authStore.updateUsername(usernameInput.value.trim())
  } catch (e) {
    profileError.value = e.message
  } finally {
    savingUsername.value = false
  }
}

async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  profileError.value = ''
  try {
    await authStore.uploadAvatar(file)
  } catch (err) {
    profileError.value = err.message
  }
  e.target.value = ''
}

async function handleCancel() {
  if (!confirm('确定取消订阅？当前周期结束后将不再续费。')) return
  membershipError.value = ''
  canceling.value = true
  try {
    await membershipStore.cancelSubscription()
    await authStore.fetchUser()
  } catch (e) {
    membershipError.value = e.message
  } finally {
    canceling.value = false
  }
}

onMounted(async () => {
  usernameInput.value = authStore.userName || ''
  loading.value = true
  try {
    await authStore.fetchUser()
    usernameInput.value = authStore.userName || ''
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.gradient-text {
  background: linear-gradient(135deg, #6C63FF, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
