<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>用户注册</h2>
      
      <form @submit.prevent="handleRegister" class="auth-form">
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
            placeholder="请输入密码（至少6位）"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <div v-if="localError" class="error-message">
          {{ localError }}
        </div>

        <button type="submit" :disabled="authStore.loading" class="btn-primary">
          {{ authStore.loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="auth-switch">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { refreshSessionAfterLogin } from '../utils/sessionReset'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const localError = ref('')

async function handleRegister() {
  localError.value = ''
  
  if (password.value !== confirmPassword.value) {
    localError.value = '两次输入的密码不一致'
    return
  }

  if (password.value.length < 6) {
    localError.value = '密码长度不能少于6位'
    return
  }

  try {
    await authStore.register(email.value, password.value)
    await authStore.fetchUser()
    await refreshSessionAfterLogin()
    router.push('/')
  } catch (err) {
    console.error('Register failed:', err)
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
