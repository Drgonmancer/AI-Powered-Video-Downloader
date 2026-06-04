import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { useMembershipStore } from './membership'

const API_BASE = '/api'

function resolveWebSocketUrl() {
  const apiBase = import.meta.env.VITE_API_URL
  if (apiBase) {
    const url = new URL(apiBase)
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    url.pathname = '/ws/downloads'
    url.search = ''
    url.hash = ''
    return url.toString()
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/downloads`
}

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref([])
  const parseResult = ref(null)
  const isParsing = ref(false)
  const isSummarizing = ref(false)
  const isSubmittingDownload = ref(false)
  const parseError = ref('')
  const settings = ref({})
  const wsConnected = ref(false)
  const wsStatus = ref('idle') // idle | connecting | connected | reconnecting | failed
  const lastParsedUrl = ref('')

  let ws = null
  let reconnectTimer = null
  let pingTimer = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 15

  function clearReconnectTimer() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function clearPingTimer() {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }

  function scheduleReconnect(delayMs = 3000) {
    clearReconnectTimer()
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      wsStatus.value = 'failed'
      wsConnected.value = false
      console.warn('[WS] Max reconnect attempts reached')
      return
    }
    wsStatus.value = 'reconnecting'
    wsConnected.value = false
    reconnectAttempts++
    reconnectTimer = setTimeout(connectWebSocket, delayMs)
  }

  async function connectWebSocket() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    wsStatus.value = reconnectAttempts > 0 ? 'reconnecting' : 'connecting'
    wsConnected.value = false

    try {
      const health = await fetch(`${API_BASE}/health`, { method: 'GET' })
      if (!health.ok) {
        throw new Error(`health check failed: ${health.status}`)
      }
    } catch (e) {
      console.warn('[WS] Backend not ready:', e.message)
      scheduleReconnect(4000)
      return
    }

    const wsUrl = resolveWebSocketUrl()
    console.log('[WS] Connecting to', wsUrl)

    try {
      ws = new WebSocket(wsUrl)
    } catch (e) {
      console.error('[WS] Failed to create WebSocket:', e)
      scheduleReconnect()
      return
    }

    const connectTimeout = setTimeout(() => {
      if (ws && ws.readyState === WebSocket.CONNECTING) {
        console.warn('[WS] Connect timeout')
        ws.close()
      }
    }, 10000)

    ws.onopen = () => {
      clearTimeout(connectTimeout)
      wsConnected.value = true
      wsStatus.value = 'connected'
      reconnectAttempts = 0
      clearPingTimer()
      pingTimer = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send('ping')
        }
      }, 25000)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'init') {
          if (data.data && Array.isArray(data.data)) {
            tasks.value = data.data
          }
        } else if (data.type === 'pong') {
          // keepalive ack
        } else if (data.type === 'usage' && data.data) {
          refreshUsage(data.data)
        } else if (data.id) {
          const idx = tasks.value.findIndex(t => t.id === data.id)
          if (idx >= 0) {
            const updated = { ...tasks.value[idx], ...data }
            tasks.value.splice(idx, 1, updated)
          } else {
            tasks.value.unshift({ ...data })
          }
        }
      } catch (e) {
        console.warn('[WS] Bad message:', e)
      }
    }

    ws.onclose = (event) => {
      clearTimeout(connectTimeout)
      clearPingTimer()
      wsConnected.value = false
      console.warn('[WS] Closed', event.code, event.reason)
      scheduleReconnect()
    }

    ws.onerror = () => {
      clearTimeout(connectTimeout)
      wsConnected.value = false
      console.warn('[WS] Error')
    }
  }

  async function fetchSettings() {
    try {
      const res = await fetch(`${API_BASE}/settings`)
      if (res.ok) settings.value = await res.json()
    } catch (e) {
      console.warn('[Store] Backend not available, using default settings')
      settings.value = {
        download_path: '',
        output_format: 'mp4',
        default_quality: 'best',
        max_concurrent: 3,
        speed_limit: 0,
        cookies: '',
        cookies_from_browser: 'edge',
        locale: 'zh',
      }
    }
  }

  async function updateSettings(data) {
    try {
      const res = await fetch(`${API_BASE}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (res.ok) settings.value = await res.json()
    } catch (e) {
      console.warn('[Store] Failed to save settings, storing locally')
      settings.value = { ...settings.value, ...data }
    }
  }

  async function parseUrl(url) {
    isParsing.value = true
    isSummarizing.value = false
    parseError.value = ''
    parseResult.value = null
    lastParsedUrl.value = url
    try {
      const res = await fetch(`${API_BASE}/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Parse failed' }))
        throw new Error(err.detail || 'Parse failed')
      }
      const info = await res.json()
      parseResult.value = info
      isParsing.value = false
      // AI 分析后台执行，不阻塞解析完成后的预览与下载
      runSummarizeInBackground(url, info)
    } catch (e) {
      parseError.value = e.message
      isParsing.value = false
      isSummarizing.value = false
    }
  }

  function refreshUsage(usageData) {
    const ms = useMembershipStore()
    if (usageData) {
      ms.applyUsage(usageData)
    } else {
      ms.fetchUsage()
    }
  }

  async function runSummarizeInBackground(url, info) {
    isSummarizing.value = true
    try {
      const authStore = useAuthStore()
      const sumHeaders = { 'Content-Type': 'application/json' }
      if (authStore.token) {
        sumHeaders['Authorization'] = `Bearer ${authStore.token}`
      }
      const sumRes = await fetch(`${API_BASE}/summarize`, {
        method: 'POST',
        headers: sumHeaders,
        body: JSON.stringify({ url, video_info: info }),
      })
      if (sumRes.ok) {
        const summary = await sumRes.json()
        if (parseResult.value) parseResult.value = { ...parseResult.value, summary }
      } else {
        const err = await sumRes.json().catch(() => ({}))
        const msg = err.detail || err.message || 'AI 分析请求失败'
        if (parseResult.value) {
          parseResult.value = {
            ...parseResult.value,
            summary: { enabled: false, summary: '', mindmap: '', transcript: '', message: msg },
          }
        }
      }
    } catch (sumErr) {
      if (parseResult.value) {
        parseResult.value = {
          ...parseResult.value,
          summary: { enabled: false, summary: '', mindmap: '', transcript: '', message: sumErr.message || 'AI 分析失败' },
        }
      }
    } finally {
      isSummarizing.value = false
    }
  }

  async function startDownload(options) {
    const authStore = useAuthStore()
    const membershipStore = useMembershipStore()
    if (isSubmittingDownload.value) return { error: '正在提交下载，请稍候' }
    isSubmittingDownload.value = true
    if (authStore.token) {
      membershipStore.optimisticUseDownload()
    }
    try {
      const headers = { 'Content-Type': 'application/json' }

      if (authStore.token) {
        headers['Authorization'] = `Bearer ${authStore.token}`
      }

      const res = await fetch(`${API_BASE}/download`, {
        method: 'POST',
        headers,
        body: JSON.stringify(options),
      })
      const data = await res.json().catch(() => ({ error: 'Request failed' }))
      if (res.status === 429) {
        await refreshUsage()
        return { error: data.detail || '今日下载次数已用完' }
      }
      if (res.ok) {
        await refreshUsage(data.usage || null)
      } else if (authStore.token) {
        await refreshUsage()
      }
      return data
    } catch (e) {
      if (authStore.token) await refreshUsage()
      return { error: e.message }
    } finally {
      isSubmittingDownload.value = false
    }
  }

  async function regenerateMindmap() {
    if (!parseResult.value) return { error: '请先解析视频' }
    isSummarizing.value = true
    try {
      const authStore = useAuthStore()
      const headers = { 'Content-Type': 'application/json' }
      if (authStore.token) {
        headers['Authorization'] = `Bearer ${authStore.token}`
      }
      const res = await fetch(`${API_BASE}/summarize`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          url: lastParsedUrl.value,
          video_info: parseResult.value,
          mode: 'mindmap',
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.detail || data.message || '生成失败')
      }
      const prev = parseResult.value.summary || {}
      parseResult.value = {
        ...parseResult.value,
        summary: {
          ...prev,
          ...data,
          enabled: data.enabled !== false,
        },
      }
      return data
    } catch (e) {
      return { error: e.message }
    } finally {
      isSummarizing.value = false
    }
  }

  async function batchDownload(playlistUrl, options = {}) {
    try {
      const body = playlistUrl ? { playlist_url: playlistUrl, ...options } : options
      const res = await fetch(`${API_BASE}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      return await res.json().catch(() => ({ error: 'Batch request failed' }))
    } catch (e) {
      return { error: e.message }
    }
  }

  async function pauseTask(taskId) {
    try {
      await fetch(`${API_BASE}/download/${taskId}/pause`, { method: 'POST' })
    } catch (e) {}
  }

  async function resumeTask(taskId) {
    try {
      await fetch(`${API_BASE}/download/${taskId}/resume`, { method: 'POST' })
    } catch (e) {}
  }

  async function cancelTask(taskId) {
    try {
      await fetch(`${API_BASE}/download/${taskId}`, { method: 'DELETE' })
      tasks.value = tasks.value.filter(t => t.id !== taskId)
    } catch (e) {}
  }

  async function convertFile(inputPath, outputFormat, quality = 'medium') {
    try {
      const res = await fetch(`${API_BASE}/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_path: inputPath, output_format: outputFormat, quality }),
      })
      return await res.json()
    } catch (e) {
      return { success: false, error: e.message }
    }
  }

  const activeTasks = computed(() =>
    tasks.value.filter(t => ['queued', 'downloading', 'merging', 'paused'].includes(t.status))
  )
  const completedTasks = computed(() =>
    tasks.value.filter(t => t.status === 'completed')
  )

  const wsStatusLabel = computed(() => {
    switch (wsStatus.value) {
      case 'connected': return 'connected'
      case 'connecting': return 'connecting'
      case 'reconnecting': return 'reconnecting'
      case 'failed': return 'failed'
      default: return 'disconnected'
    }
  })

  function init() {
    reconnectAttempts = 0
    connectWebSocket()
    fetchSettings()
  }

  function reconnect() {
    disconnect()
    reconnectAttempts = 0
    connectWebSocket()
  }

  function disconnect() {
    clearReconnectTimer()
    clearPingTimer()
    if (ws) {
      ws.onclose = null
      ws.onerror = null
      ws.close()
      ws = null
    }
    wsConnected.value = false
    wsStatus.value = 'idle'
  }

  function resetSession() {
    disconnect()
    tasks.value = []
    parseResult.value = null
    parseError.value = ''
    reconnectAttempts = 0
  }

  return {
    tasks, parseResult, isParsing, isSummarizing, isSubmittingDownload, parseError,
    settings, wsConnected, wsStatus, wsStatusLabel, lastParsedUrl,
    activeTasks, completedTasks,
    init, disconnect, reconnect, resetSession,
    parseUrl, startDownload, batchDownload, regenerateMindmap,
    pauseTask, resumeTask, cancelTask,
    convertFile, fetchSettings, updateSettings,
  }
})
