<template>
  <div class="max-w-2xl mx-auto py-8 px-4 space-y-6">
    <h1 class="text-2xl font-bold">
      <span class="gradient-text">个人中心</span>
    </h1>

    <!-- Profile -->
    <section class="rounded-2xl border border-white/10 bg-[#1A1A2E] p-6 space-y-4">
      <div class="flex items-center gap-4">
        <img
          v-if="authStore.userAvatar"
          :src="authStore.userAvatar"
          alt="avatar"
          class="w-16 h-16 rounded-full object-cover ring-2 ring-[#6C63FF]/50"
        />
        <div
          v-else
          class="w-16 h-16 rounded-full bg-gradient-to-br from-[#6C63FF] to-purple-600 flex items-center justify-center text-white text-xl font-bold"
        >
          {{ authStore.userName?.charAt(0)?.toUpperCase() || '?' }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-white font-semibold truncate">{{ authStore.userName || '未设置昵称' }}</p>
          <p class="text-gray-500 text-sm truncate">{{ authStore.userEmail }}</p>
        </div>
        <label class="cursor-pointer px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 hover:border-[#6C63FF]/30 text-gray-300">
          更换头像
          <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
        </label>
      </div>

      <div class="flex gap-2">
        <input
          v-model="usernameInput"
          type="text"
          placeholder="用户名"
          class="flex-1 px-4 py-2 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50"
        />
        <button
          class="px-4 py-2 rounded-xl text-sm font-medium text-white bg-[#6C63FF] hover:bg-[#5a52e0] disabled:opacity-50"
          :disabled="savingUsername"
          @click="saveUsername"
        >
          {{ savingUsername ? '保存中' : '保存' }}
        </button>
      </div>
      <p v-if="profileError" class="text-red-400 text-xs">{{ profileError }}</p>
    </section>

    <!-- Membership -->
    <section class="rounded-2xl border border-white/10 bg-[#1A1A2E] p-6 space-y-4">
      <h2 class="text-sm font-bold text-gray-300 uppercase tracking-wider">会员状态</h2>
      <div class="flex items-center justify-between">
        <span class="text-gray-400 text-sm">当前套餐</span>
        <span class="text-white font-semibold">{{ planLabel }}</span>
      </div>
      <div v-if="membershipStore.currentPeriodEnd" class="flex items-center justify-between">
        <span class="text-gray-400 text-sm">到期时间</span>
        <span class="text-gray-300 text-sm">{{ membershipStore.currentPeriodEnd }}</span>
      </div>
      <div v-if="membershipStore.cancelAtPeriodEnd" class="text-yellow-400 text-xs">
        已申请取消，将在当前周期结束后失效
      </div>
      <div class="flex gap-3 pt-2">
        <router-link
          to="/pricing"
          class="flex-1 text-center py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#6C63FF] to-[#3B82F6]"
        >
          升级套餐
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
const profileError = ref('')
const membershipError = ref('')

const planLabel = computed(() => {
  const map = { free: '免费版', basic: '基础版', pro: '专业版' }
  return map[membershipStore.currentPlan] || membershipStore.currentPlan
})

const canCancel = computed(() =>
  membershipStore.isActive &&
  membershipStore.currentPlan !== 'free' &&
  !membershipStore.cancelAtPeriodEnd
)

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
}

async function handleCancel() {
  if (!confirm('确定取消订阅？当前周期结束后将不再续费。')) return
  membershipError.value = ''
  canceling.value = true
  try {
    await membershipStore.cancelSubscription()
  } catch (e) {
    membershipError.value = e.message
  } finally {
    canceling.value = false
  }
}

onMounted(async () => {
  usernameInput.value = authStore.userName || ''
  await membershipStore.fetchMembershipStatus()
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
