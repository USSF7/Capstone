<script setup>
/**
 * Authentication logout functions
 * @module AuthLogout
 */

import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

/**
 * Vue Router instance for navigation.
 */
const router = useRouter()

/**
 * Auth store managing user session and tokens.
 */
const auth = useAuthStore()

/**
 * Clears authentication, which includes tokens and user data. Redirects the user to the login page.
 */
onMounted(() => {
  auth.clearAuth()
  router.push('/login')
})
</script>

<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <p class="text-gray-600">Signing out...</p>
  </div>
</template>
