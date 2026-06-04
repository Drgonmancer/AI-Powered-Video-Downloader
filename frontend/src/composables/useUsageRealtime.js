import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useMembershipStore } from '../stores/membership'

const POLL_MS = 30000

/** 全局用量同步：WebSocket 事件 + 定时拉取 + 自定义事件 */
export function useUsageRealtime() {
  const authStore = useAuthStore()
  const membershipStore = useMembershipStore()
  let timer = null

  function onUsageEvent(e) {
    if (e.detail) membershipStore.applyUsage(e.detail)
  }

  function refreshIfLoggedIn() {
    if (authStore.token) membershipStore.fetchUsage()
  }

  onMounted(() => {
    window.addEventListener('app:usage-updated', onUsageEvent)
    refreshIfLoggedIn()
    timer = setInterval(refreshIfLoggedIn, POLL_MS)
  })

  onUnmounted(() => {
    window.removeEventListener('app:usage-updated', onUsageEvent)
    if (timer) clearInterval(timer)
  })
}
