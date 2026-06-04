import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

// 会话不持久化：刷新或重启浏览器后必须重新登录
localStorage.removeItem('token')

const app = createApp(App)
app.config.errorHandler = (err, _instance, info) => {
  console.error('[Vue Error]', err, info)
}
app.use(createPinia())
app.use(router)
app.mount('#app')
