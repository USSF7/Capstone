/**
 * API Client for communicating with the backend
 */

const API_BASE_URL = 'http://localhost:5000/api'

class ApiClient {
  _refreshing = null

  async _refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    })

    if (!response.ok) return false

    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user))
    }
    return true
  }

  async request(endpoint, options = {}, _retried = false) {
    const url = `${API_BASE_URL}${endpoint}`
    const token = localStorage.getItem('access_token')
    const isFormData = options.body instanceof FormData
    const config = {
      headers: {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (response.status === 401 && !_retried) {
        if (!this._refreshing) {
          this._refreshing = this._refreshToken().finally(() => { this._refreshing = null })
        }
        const refreshed = await this._refreshing
        if (refreshed) {
          return this.request(endpoint, options, true)
        }
        // Refresh failed — clear auth and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        throw new Error('Session expired')
      }

      if (!response.ok) {
        let message = `HTTP ${response.status}`
        try {
          const error = await response.json()
          message = error.error || message
        } catch {
          // Response was not JSON (e.g. HTML error page)
        }
        throw new Error(message)
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error: ${error.message}`)
      throw error
    }
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  postForm(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
    })
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  delete(endpoint, data = {}) {
    return this.request(endpoint, { 
      method: 'DELETE',
      body: JSON.stringify(data) 
    })
  }
}

export default new ApiClient()