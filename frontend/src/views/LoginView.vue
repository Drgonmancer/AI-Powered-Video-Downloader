<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>用户登录</h2>

      <div v-if="alreadyLoggedIn" class="logged-in-banner">
        <p>当前已登录：<strong>{{ authStore.userEmail }}</strong></p>
        <div class="banner-actions">
          <button type="button" class="btn-secondary" @click="goHome">进入首页</button>
          <button type="button" class="btn-outline" @click="switchAccount">退出并切换账号</button>
        </div>
      </div>

      <form v-else @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="请输入邮箱"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button type="submit" :disabled="authStore.loading" class="btn-primary">
          {{ authStore.loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p v-if="!alreadyLoggedIn" class="auth-switch">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { refreshSessionAfterLogin, clearSessionOnLogout } from '../utils/sessionReset'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const switching = ref(false)

const alreadyLoggedIn = computed(() => authStore.isLoggedIn && !switching.value)

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }
})

function goHome() {
  router.push('/')
}

async function switchAccount() {
  switching.value = true
  authStore.logout()
  await clearSessionOnLogout()
  email.value = ''
  password.value = ''
  authStore.error = ''
}

async function handleLogin() {
  if (!email.value || !password.value) {
    authStore.error = '请输入邮箱和密码'
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    authStore.error = '请输入有效的邮箱地址'
    return
  }

  try {
    await authStore.login(email.value, password.value)
    await refreshSessionAfterLogin()
    switching.value = false
    router.push('/')
  } catch (err) {
    console.error('Login failed:', err)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.auth-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-card h2 {
  margin: 0 0 24px;
  text-align: center;
  color: var(--text-primary);
}

.logged-in-banner {
  text-align: center;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  margin-bottom: 8px;
}

.logged-in-banner p {
  margin: 0 0 16px;
  color: var(--text-primary);
  font-size: 14px;
}

.banner-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-group input:focus {
  outline: none;
  border-color: #6C63FF;
}

.error-message {
  color: #ef4444;
  font-size: 14px;
  padding: 8px;
  background: #fef2f2;
  border-radius: 6px;
}

.btn-primary {
  padding: 12px;
  background: #6C63FF;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #5a52e0;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 16px;
  background: #6C63FF;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-outline {
  padding: 10px 16px;
  background: transparent;
  color: #6C63FF;
  border: 2px solid #6C63FF;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-switch a {
  color: #6C63FF;
  text-decoration: none;
  font-weight: 500;
}

.auth-switch a:hover {
  text-decoration: underline;
}
</style>
