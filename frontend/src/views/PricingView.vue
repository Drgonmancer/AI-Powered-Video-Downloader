<template>
  <div class="max-w-5xl mx-auto py-8 px-4">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-bold mb-2">
        <span class="gradient-text">会员套餐</span>
      </h1>
      <p class="text-gray-500 text-sm">解锁更多下载次数与 AI 功能</p>
    </div>

    <div v-if="loading" class="text-center text-gray-500 py-12">加载中...</div>

    <div v-else class="grid gap-6 md:grid-cols-3">
      <div
        v-for="(item, key) in planCards"
        :key="key"
        class="rounded-2xl border p-6 flex flex-col transition-all"
        :class="key === 'pro'
          ? 'border-[#6C63FF]/40 bg-gradient-to-b from-[#6C63FF]/10 to-transparent'
          : 'border-white/10 bg-[#1A1A2E]'"
      >
        <h3 class="text-lg font-bold text-white mb-1">{{ item.name }}</h3>
        <div class="mb-4">
          <span class="text-3xl font-bold text-white">
            {{ item.price === 0 ? '免费' : `¥${(item.price / 100).toFixed(0)}` }}
          </span>
          <span v-if="item.price > 0" class="text-gray-500 text-sm">/月</span>
        </div>
        <ul class="space-y-2 text-sm text-gray-400 flex-1 mb-6">
          <li>每日下载 {{ formatLimit(item.features?.max_downloads_per_day) }}</li>
          <li>最高画质 {{ item.features?.max_quality || '-' }}</li>
          <li>AI 摘要 {{ formatLimit(item.features?.max_ai_summaries_per_day) }}</li>
          <li>{{ item.features?.batch_download ? '支持批量下载' : '不支持批量' }}</li>
        </ul>
        <button
          v-if="key === 'free'"
          disabled
          class="w-full py-2.5 rounded-xl text-sm font-medium bg-white/5 text-gray-500 cursor-not-allowed"
        >
          当前方案
        </button>
        <button
          v-else
          :disabled="checkoutLoading === key || isCurrentPlan(key)"
          class="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-opacity"
          :class="key === 'pro'
            ? 'bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] hover:opacity-90'
            : 'bg-[#6C63FF] hover:bg-[#5a52e0]'"
          @click="handleCheckout(key)"
        >
          {{ checkoutLoading === key ? '跳转中...' : isCurrentPlan(key) ? '已订阅' : '立即开通' }}
        </button>
      </div>
    </div>

    <p v-if="error" class="mt-6 text-center text-red-400 text-sm">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { membershipApi } from '../api/membershipApi'
import { useMembershipStore } from '../stores/membership'
import { useAuthStore } from '../stores/auth'

const membershipStore = useMembershipStore()
const authStore = useAuthStore()

const loading = ref(true)
const plans = ref({})
const error = ref('')
const checkoutLoading = ref('')

const planCards = computed(() => plans.value || {})

function formatLimit(n) {
  if (n === -1) return '无限'
  return n ?? '-'
}

function isCurrentPlan(key) {
  return membershipStore.currentPlan === key && membershipStore.isActive
}

async function handleCheckout(plan) {
  error.value = ''
  checkoutLoading.value = plan
  try {
    await membershipStore.createCheckout(plan)
  } catch (e) {
    error.value = e.message
    checkoutLoading.value = ''
  }
}

onMounted(async () => {
  try {
    const res = await membershipApi.getPlans()
    plans.value = res.data?.plans || {}
    await membershipStore.fetchMembershipStatus()
  } catch (e) {
    error.value = e.message
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
