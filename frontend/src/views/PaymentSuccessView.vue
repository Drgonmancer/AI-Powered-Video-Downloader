<template>
  <div class="flex justify-center items-center min-h-[60vh] px-4">
    <div class="w-full max-w-md rounded-2xl border border-white/10 bg-[#1A1A2E] p-8 text-center">
      <div v-if="verifying" class="space-y-4">
        <div class="w-12 h-12 mx-auto border-2 border-[#6C63FF] border-t-transparent rounded-full animate-spin"></div>
        <p class="text-gray-400">正在验证支付...</p>
      </div>

      <div v-else-if="verified" class="space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 flex items-center justify-center">
          <svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-xl font-bold text-white">支付成功</h2>
        <p class="text-gray-400 text-sm">您已开通 {{ planLabel }} 会员</p>
        <router-link
          to="/"
          class="inline-block mt-4 px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#6C63FF] to-[#3B82F6]"
        >
          返回首页
        </router-link>
      </div>

      <div v-else class="space-y-4">
        <p class="text-yellow-400 text-sm">{{ message || '支付验证未完成，请稍后刷新会员状态' }}</p>
        <router-link to="/member/center" class="text-[#6C63FF] text-sm hover:underline">前往会员中心</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { membershipApi } from '../api/membershipApi'
import { useAuthStore } from '../stores/auth'
import { useMembershipStore } from '../stores/membership'

const route = useRoute()
const authStore = useAuthStore()
const membershipStore = useMembershipStore()

const verifying = ref(true)
const verified = ref(false)
const message = ref('')
const plan = ref('')

const planLabel = computed(() => {
  const map = { basic: '基础版', pro: '专业版', free: '免费' }
  return map[plan.value] || plan.value
})

onMounted(async () => {
  const sessionId = route.query.session_id
  if (!sessionId || !authStore.token) {
    verifying.value = false
    message.value = '缺少支付会话或尚未登录'
    return
  }
  try {
    const res = await membershipApi.verifySession(authStore.token, sessionId)
    if (res.data?.verified) {
      verified.value = true
      plan.value = res.data.plan || ''
      await membershipStore.fetchMembershipStatus()
    } else {
      message.value = '支付尚未完成，请稍后再试'
    }
  } catch (e) {
    message.value = e.message
  } finally {
    verifying.value = false
  }
})
</script>
