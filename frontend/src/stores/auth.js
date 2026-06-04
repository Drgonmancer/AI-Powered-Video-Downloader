import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/authApi'
import { useMembershipStore } from './membership'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  // 仅内存保存，刷新/关闭页面后须重新登录
  const token = ref('')
  const loading = ref(false)
  const error = ref('')

  const isLoggedIn = computed(() => !!token.value)
  const userEmail = computed(() => user.value?.email || '')
  const userName = computed(() => user.value?.username || user.value?.name || '')
  const userAvatar = computed(() => user.value?.avatar || '')
  const role = computed(() => user.value?.role || 'user')
  const roleLabel = computed(() => user.value?.role_label || '普通用户')
  const isVip = computed(() => !!user.value?.is_vip)
  const planName = computed(() => user.value?.plan_name || '免费版')
  const membership = computed(() => user.value?.membership || null)
  const usage = computed(() => user.value?.usage || null)
  const usageCount = computed(() => user.value?.usage_count ?? user.value?.usage?.downloads?.used ?? 0)

  async function register(email, password) {
    loading.value = true
    error.value = ''
    try {
      const response = await authApi.register(email, password)
      token.value = response.data.token
      user.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = ''
    try {
      const response = await authApi.login(email, password)
      token.value = response.data.token
      user.value = response.data
      await fetchUser()
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    
    try {
      const response = await authApi.getMe(token.value)
      user.value = response.data
      useMembershipStore().syncFromProfile(response.data)
    } catch (err) {
      console.error('Failed to fetch user:', err)
      logout()
    }
  }

  async function updateProfile(data) {
    if (!token.value) return
    
    try {
      const response = await authApi.updateProfile(token.value, data)
      user.value = { ...user.value, ...response.data }
      return response
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function uploadAvatar(file) {
    if (!token.value) return
    
    try {
      const response = await authApi.uploadAvatar(token.value, file)
      user.value = response.data?.id ? response.data : { ...user.value, ...response.data }
      useMembershipStore().syncFromProfile(user.value)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function updateUsername(username) {
    if (!token.value) return
    
    try {
      const response = await authApi.updateUsername(token.value, username)
      user.value = response.data?.membership ? response.data : { ...user.value, ...response.data }
      useMembershipStore().syncFromProfile(user.value)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    error.value = ''
    localStorage.removeItem('token')
  }

  function init() {
    // 清除旧版本写入 localStorage 的 token，避免升级后仍被恢复登录
    localStorage.removeItem('token')
    if (token.value) {
      fetchUser()
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isLoggedIn,
    userEmail,
    userName,
    userAvatar,
    role,
    roleLabel,
    isVip,
    planName,
    membership,
    usage,
    usageCount,
    register,
    login,
    fetchUser,
    logout,
    init,
    updateProfile,
    uploadAvatar,
    updateUsername
  }
})
