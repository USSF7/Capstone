<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import authService from '../../services/authService'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

onMounted(async () => {
  const accessToken = route.query.access_token
  const refreshToken = route.query.refresh_token

  if (accessToken && refreshToken) {
    auth.setAuth({ access_token: accessToken, refresh_token: refreshToken })

    // Fetch user info now that we have a token
    try {
      const user = await authService.getMe()
      auth.setAuth({ access_token: accessToken, refresh_token: refreshToken, user })
    } catch {
      // Token is stored; user info will load on next page
    }

    router.push('/')
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
