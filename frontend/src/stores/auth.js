import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/authApi'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const loading = ref(false)
  const error = ref('')

  const isLoggedIn = computed(() => !!token.value)
  const userEmail = computed(() => user.value?.email || '')
  const userName = computed(() => user.value?.username || user.value?.name || '')
  const userAvatar = computed(() => user.value?.avatar || '')
  const role = computed(() => user.value?.role || 'user')
  const usageCount = computed(() => user.value?.usage_count || 0)

  async function register(email, password) {
    loading.value = true
    error.value = ''
    try {
      const response = await authApi.register(email, password)
      token.value = response.data.token
      user.value = response.data
      localStorage.setItem('token', response.data.token)
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
      localStorage.setItem('token', response.data.token)
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
      user.value = { ...user.value, avatar: response.data.avatar }
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
      user.value = { ...user.value, username: response.data.username }
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
