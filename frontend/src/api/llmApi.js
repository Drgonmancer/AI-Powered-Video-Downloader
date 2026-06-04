const BASE = '/api/llm'

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = data.detail
    let msg = typeof detail === 'string' ? detail : data.message
    if (res.status === 405) {
      msg = '接口未就绪，请关闭后端窗口后重新运行「一键启动.bat」'
    } else if (res.status === 404 && typeof detail === 'string' && detail.includes('Route not found')) {
      msg = '大模型 API 未加载，请重启后端（一键启动.bat）'
    }
    throw new Error(msg || `请求失败 (${res.status})`)
  }
  return data
}

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

export const llmApi = {
  async list(token) {
    const res = await fetch(`${BASE}/providers`, { headers: authHeaders(token) })
    return handleResponse(res)
  },

  async create(token, payload) {
    const res = await fetch(`${BASE}/providers`, {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    })
    return handleResponse(res)
  },

  async remove(token, id) {
    const res = await fetch(`${BASE}/providers/${id}`, {
      method: 'DELETE',
      headers: authHeaders(token),
    })
    return handleResponse(res)
  },

  async setDefault(token, id) {
    const res = await fetch(`${BASE}/providers/${id}/default`, {
      method: 'POST',
      headers: authHeaders(token),
    })
    return handleResponse(res)
  },
}
