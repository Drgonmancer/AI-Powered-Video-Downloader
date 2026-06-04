import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { membershipApi } from '../api/membershipApi'
import { useAuthStore } from './auth'

export const useMembershipStore = defineStore('membership', () => {
  const plan = ref('free')
  const status = ref('active')
  const isActive = ref(true)
  const currentPeriodStart = ref(null)
  const currentPeriodEnd = ref(null)
  const cancelAtPeriodEnd = ref(false)
  const loading = ref(false)
  const error = ref('')

  const dailyUsed = ref(0)
  const dailyLimit = ref(5)
  const dailyRemaining = ref(5)
  const isUnlimited = ref(false)
  const resetsAt = ref('')
  const usageDate = ref('')
  const usageRevision = ref(0)

  const currentPlan = computed(() => plan.value || 'free')
  const isPro = computed(() => currentPlan.value === 'pro' && isActive.value)
  const isBasic = computed(() => currentPlan.value === 'basic' && isActive.value)

  const membershipTimeRemaining = computed(() => {
    if (!currentPeriodEnd.value || currentPlan.value === 'free') return ''
    const end = new Date(currentPeriodEnd.value.replace(' ', 'T'))
    if (Number.isNaN(end.getTime())) return ''
    const diff = end - Date.now()
    if (diff <= 0) return '已过期'
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
    return days <= 1 ? '即将到期' : `${days}天`
  })

  function _token() {
    return useAuthStore().token
  }

  async function fetchMembershipStatus() {
    const token = _token()
    if (!token) return
    loading.value = true
    error.value = ''
    try {
      const res = await membershipApi.getStatus(token)
      const data = res.data || {}
      plan.value = data.plan || 'free'
      status.value = data.status || 'active'
      isActive.value = data.is_active !== false
      currentPeriodStart.value = data.current_period_start || null
      currentPeriodEnd.value = data.current_period_end || null
      cancelAtPeriodEnd.value = !!data.cancel_at_period_end
    } catch (err) {
      error.value = err.message
      console.warn('[Membership]', err.message)
    } finally {
      loading.value = false
    }
  }

  async function createCheckout(planName) {
    const token = _token()
    if (!token) throw new Error('请先登录')
    const res = await membershipApi.createCheckout(token, planName)
    const url = res.data?.checkout_url
    if (!url) throw new Error('未获取到支付链接')
    window.location.href = url
    return res
  }

  function applyUsage(data) {
    if (!data) return
    dailyUsed.value = data.downloads?.used ?? 0
    dailyLimit.value = data.downloads?.limit ?? 5
    dailyRemaining.value = data.downloads?.remaining ?? 0
    isUnlimited.value = !!data.is_unlimited
    resetsAt.value = data.resets_at || ''
    usageDate.value = data.usage_date || ''
    usageRevision.value += 1

    const auth = useAuthStore()
    if (auth.user) {
      auth.$patch({
        user: {
          ...auth.user,
          usage: data,
          usage_count: data.downloads?.used ?? 0,
        },
      })
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('app:usage-updated', { detail: data }))
    }
  }

  /** 下载发起时的乐观 +1，失败时由 applyUsage 覆盖 */
  function optimisticUseDownload() {
    if (isUnlimited.value) return
    dailyUsed.value += 1
    dailyRemaining.value = Math.max(0, (dailyLimit.value || 5) - dailyUsed.value)
    usageRevision.value += 1
  }

  async function fetchUsage() {
    const token = _token()
    if (!token) return
    try {
      const res = await membershipApi.getUsage(token)
      applyUsage(res.data)
    } catch (err) {
      console.warn('[Usage]', err.message)
    }
  }

  function syncFromProfile(profile) {
    if (!profile) return
    const m = profile.membership || {}
    plan.value = m.plan || profile.plan || 'free'
    status.value = m.status || 'active'
    isActive.value = m.is_active !== false
    currentPeriodStart.value = m.current_period_start || null
    currentPeriodEnd.value = m.current_period_end || null
    cancelAtPeriodEnd.value = !!m.cancel_at_period_end
    if (profile.usage) {
      applyUsage(profile.usage)
    }
  }

  async function cancelSubscription() {
    const token = _token()
    if (!token) throw new Error('请先登录')
    const res = await membershipApi.cancelSubscription(token)
    await fetchMembershipStatus()
    return res
  }

  return {
    plan,
    status,
    isActive,
    currentPlan,
    isPro,
    isBasic,
    currentPeriodStart,
    currentPeriodEnd,
    cancelAtPeriodEnd,
    syncFromProfile,
    dailyUsed,
    dailyLimit,
    dailyRemaining,
    isUnlimited,
    resetsAt,
    usageDate,
    usageRevision,
    applyUsage,
    optimisticUseDownload,
    fetchUsage,
    membershipTimeRemaining,
    loading,
    error,
    fetchMembershipStatus,
    createCheckout,
    cancelSubscription,
  }
})
