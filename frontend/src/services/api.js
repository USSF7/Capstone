/**
 * API Client for communicating with the backend
 */

import { API_BASE_URL } from '../config/runtime'

/**
 * API Client for communicating with the backend.
 * 
 * @class ApiClient
 */
class ApiClient {
  /**
   * Tracks the current token refresh promise to prevent multiple simultaneous refresh requests.
   * 
   * @type {Promise<boolean>|null}
   * @private
   */
  _refreshing = null

  /**
   * Attempts to refresh the access token using the refresh token.
   * 
   * @returns {Promise<boolean>} Returns true if refresh succeeded, false otherwise
   * 
   * @private
   */
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

  /**
   * Core request handler used by all HTTP methods.
   * 
   * @param {string} endpoint - API endpoint 
   * @param {RequestInit} [options={}] - Fetch configuration options
   * @param {boolean} [_retried=false] - Internal flag to prevent infinite retry loops
   * 
   * @returns {Promise<any>} Parsed JSON response from the API
   * 
   * @throws {Error} If request fails or server returns an error response
   */
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

  /**
   * Sends a GET request.
   * 
   * @param {string} endpoint - API endpoint
   * @returns {Promise<any>}
   */
  get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * Sends a POST request with JSON payload.
   * 
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<any>}
   */
  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  /**
   * Sends a POST request with FormData
   * 
   * @param {string} endpoint - API endpoint
   * @param {FormData} formData - FormData payload
   * @returns {Promise<any>}
   */
  postForm(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
    })
  }

  /**
   * Sends a PUT request with JSON payload.
   * 
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<any>}
   */
  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  /**
   * Sends a DELETE request.
   * 
   * @param {string} endpoint - API endpoint
   * @param {Object} [data={}] - Optional request body
   * @returns {Promise<any>}
   */
  delete(endpoint, data = {}) {
    return this.request(endpoint, { 
      method: 'DELETE',
      body: JSON.stringify(data) 
    })
  }
}

export default new ApiClient()
