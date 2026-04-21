/**
 * Authentication functions for managing user authentication.
 * @module StoresAuth
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

/**
 * Pinia store for managing authentication state across the application.
 */
export const useAuthStore = defineStore('auth', () => {
  /**
   * Currently authenticated user object.
   * Initialized from localStorage to persist sessions across reloads.
   * 
   * @type {Ref<Object|null>}
   */
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  /**
   * JWT access token used for authenticated API requests.
   * 
   * @type {Ref<string|null>}
   */
  const accessToken = ref(localStorage.getItem('access_token') || null)

  /**
   * JWT refresh token used to obtain new access tokens.
   * 
   * @type {Ref<string|null>}
   */
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)

  /**
   * Indicates whether the user is currently authenticated.
   * 
   * @returns {boolean} True if an access token exists
   */
  const isAuthenticated = computed(() => !!accessToken.value)

  /**
   * Indicates whether the user's profile is fully completed.
   * 
   * @returns {boolean} True if user exists and profile_complete flag is set
   */
  const profileComplete = computed(() => !!user.value?.profile_complete)

  /**
   * Sets authentication state after login or token refresh.
   * Also persists data to localStorage for session persistence.
   * 
   * @param {Object} tokens - Authentication payload from backend
   * @param {string} tokens.access_token - JWT access token
   * @param {string} tokens.refresh_token - JWT refresh token
   * @param {Object} [tokens.user] - Authenticated user object
   */
  function setAuth(tokens) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    user.value = tokens.user || null

    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    if (tokens.user) {
      localStorage.setItem('user', JSON.stringify(tokens.user))
    }
  }

  /**
   * Clears all authentication state (logout).
   * Removes tokens and user data from both reactive state and localStorage.
   */
  function clearAuth() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return { user, accessToken, refreshToken, isAuthenticated, profileComplete, setAuth, clearAuth }
})
