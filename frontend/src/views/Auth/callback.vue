<script setup>
/**
 * Authentication callback functions
 * @module AuthCallback
 */

import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import authService from '../../services/authService'

/**
 * Vue Router instance for navigation.
 */
const router = useRouter()

/**
 * Current route containing query parameters.
 */
const route = useRoute()

/**
 * Auth store for persisting tokens and user state.
 */
const auth = useAuthStore()

/**
 * The component extracts access and refresh tokens from URL,
 * stores tokens in auth store, fetches current user profile, and
 * redirects based on profile completion.
 */
onMounted(async () => {
  const accessToken = route.query.access_token
  const refreshToken = route.query.refresh_token

  if (accessToken && refreshToken) {
    auth.setAuth({ access_token: accessToken, refresh_token: refreshToken })

    // Fetch user info now that we have a token
    try {
      const user = await authService.getMe()
      auth.setAuth({ access_token: accessToken, refresh_token: refreshToken, user })

      if (user.profile_complete) {
        router.push('/')
      } else {
        router.push('/profile/create')
      }
    } catch {
      // Token is stored; redirect to profile completion to be safe
      router.push('/profile/create')
    }
  } else {
    router.push('/login')
  }
})
</script>

<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <p class="text-gray-600">Signing you in...</p>
  </div>
</template>
