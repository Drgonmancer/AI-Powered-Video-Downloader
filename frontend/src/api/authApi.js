const BASE = '/api/auth'

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = data.detail
    const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0]?.msg : data.message
    throw new Error(msg || '请求失败')
  }
  return data
}

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
  }
}

export const authApi = {
  async register(email, password) {
    const res = await fetch(`${BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    return handleResponse(res)
  },

  async login(email, password) {
    const res = await fetch(`${BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    return handleResponse(res)
  },

  async getMe(token) {
    const res = await fetch(`${BASE}/me`, {
      headers: authHeaders(token),
    })
    return handleResponse(res)
  },

  async updateProfile(token, data) {
    const res = await fetch(`${BASE}/profile`, {
      method: 'PUT',
      headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse(res)
  },

  async uploadAvatar(token, file) {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE}/avatar`, {
      method: 'POST',
      headers: authHeaders(token),
      body: form,
    })
    return handleResponse(res)
  },

  async updateUsername(token, username) {
    const res = await fetch(`${BASE}/username`, {
      method: 'PUT',
      headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
      body: JSON.stringify({ username }),
    })
    return handleResponse(res)
  },
}
