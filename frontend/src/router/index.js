import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SettingsView from '../views/SettingsView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PricingView from '../views/PricingView.vue'
import PaymentSuccessView from '../views/PaymentSuccessView.vue'
import PaymentCancelView from '../views/PaymentCancelView.vue'
import MemberCenterView from '../views/MemberCenterView.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { requiresAuth: false } },
  { path: '/register', name: 'register', component: RegisterView, meta: { requiresAuth: false } },
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/settings', name: 'settings', component: SettingsView, meta: { requiresAuth: true } },
  { path: '/pricing', name: 'pricing', component: PricingView, meta: { requiresAuth: true } },
  { path: '/payment/success', name: 'payment-success', component: PaymentSuccessView, meta: { requiresAuth: true } },
  { path: '/payment/cancel', name: 'payment-cancel', component: PaymentCancelView, meta: { requiresAuth: true } },
  { path: '/member/center', name: 'member-center', component: MemberCenterView, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

let isFirstNavigation = true

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (isFirstNavigation) {
    isFirstNavigation = false

    if (authStore.token) {
      try {
        await authStore.fetchUser()
      } catch (e) {
        authStore.logout()
      }
    }

    if (!authStore.isLoggedIn && to.path !== '/login' && to.path !== '/register') {
      next('/login')
      return
    }
  }

  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && authStore.isLoggedIn) {
    // 已登录也可进入登录页，用于切换账号（见 LoginView）
    next()
  } else {
    next()
  }
})

export default router
