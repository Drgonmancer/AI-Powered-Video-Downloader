import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { membershipApi } from '../api/membershipApi'
import { useAuthStore } from './auth'

export const useMembershipStore = defineStore('membership', () => {
  const plan = ref('free')
  const status = ref('active')
  const isActive = ref(true)
  const currentPeriodEnd = ref(null)
  const cancelAtPeriodEnd = ref(false)
  const loading = ref(false)
  const error = ref('')

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
    currentPeriodEnd,
    cancelAtPeriodEnd,
    membershipTimeRemaining,
    loading,
    error,
    fetchMembershipStatus,
    createCheckout,
    cancelSubscription,
  }
})
