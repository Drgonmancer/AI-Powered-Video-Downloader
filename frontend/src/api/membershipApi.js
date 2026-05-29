const BASE = '/api/membership'

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = data.detail
    const msg = typeof detail === 'string' ? detail : data.message
    throw new Error(msg || '请求失败')
  }
  return data
}

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` }
}

export const membershipApi = {
  async getPlans() {
    const res = await fetch(`${BASE}/plans`)
    return handleResponse(res)
  },

  async getStatus(token) {
    const res = await fetch(`${BASE}/status`, { headers: authHeaders(token) })
    return handleResponse(res)
  },

  async createCheckout(token, plan) {
    const res = await fetch(`${BASE}/checkout`, {
      method: 'POST',
      headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan }),
    })
    return handleResponse(res)
  },

  async cancelSubscription(token) {
    const res = await fetch(`${BASE}/cancel`, {
      method: 'POST',
      headers: authHeaders(token),
    })
    return handleResponse(res)
  },

  async getUsage(token) {
    const res = await fetch(`${BASE}/usage`, { headers: authHeaders(token) })
    return handleResponse(res)
  },

  async verifySession(token, sessionId) {
    const res = await fetch(`${BASE}/verify-session`, {
      method: 'POST',
      headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    return handleResponse(res)
  },
}
