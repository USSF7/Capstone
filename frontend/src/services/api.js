/**
 * API Client for communicating with the backend
 */

const API_BASE_URL = 'http://localhost:5000/api'

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const token = localStorage.getItem('access_token')
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
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

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

export default new ApiClient()