import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = '/api'

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref([])
  const parseResult = ref(null)
  const isParsing = ref(false)
  const parseError = ref('')
  const settings = ref({})
  const wsConnected = ref(false)
  const lastParsedUrl = ref('')

  let ws = null
  let reconnectTimer = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 10

  function connectWebSocket() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.warn('[WS] Max reconnect attempts reached, stopping auto-reconnect')
      return
    }
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${protocol}//${location.host}/ws/downloads`)

    ws.onopen = () => {
      wsConnected.value = true
      reconnectAttempts = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'init') {
          if (data.data && Array.isArray(data.data)) {
            tasks.value = data.data
          }
        } else if (data.id) {
          const idx = tasks.value.findIndex(t => t.id === data.id)
          if (idx >= 0) {
            const updated = { ...tasks.value[idx], ...data }
            tasks.value.splice(idx, 1, updated)
          } else {
            tasks.value.unshift({ ...data })
          }
        }
      } catch (e) {}
    }

    ws.onclose = () => {
      wsConnected.value = false
      reconnectAttempts++
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectTimer = setTimeout(connectWebSocket, 3000)
      }
    }

    ws.onerror = () => {
      wsConnected.value = false
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
      parseResult.value = await res.json()
    } catch (e) {
      parseError.value = e.message
    } finally {
      isParsing.value = false
    }
  }

  async function startDownload(options) {
    try {
      const res = await fetch(`${API_BASE}/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options),
      })
      return await res.json().catch(() => ({ error: 'Request failed' }))
    } catch (e) {
      return { error: e.message }
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

  function init() {
    connectWebSocket()
    fetchSettings()
  }

  function disconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws) {
      ws.onclose = null
      ws.onerror = null
      ws.close()
    }
  }

  return {
    tasks, parseResult, isParsing, parseError,
    settings, wsConnected, lastParsedUrl,
    activeTasks, completedTasks,
    init, disconnect,
    parseUrl, startDownload, batchDownload,
    pauseTask, resumeTask, cancelTask,
    convertFile, fetchSettings, updateSettings,
  }
})
