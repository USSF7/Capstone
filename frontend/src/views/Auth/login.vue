<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import authService from '../../services/authService'

const router = useRouter()
const auth = useAuthStore()

const isRegister = ref(false)
const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    let tokens
    if (isRegister.value) {
      tokens = await authService.register(name.value, email.value, password.value)
    } else {
      tokens = await authService.login(email.value, password.value)
    }
    auth.setAuth(tokens)
    router.push('/')
  } catch (e) {
    error.value = e.message || 'Something went wrong'
  } finally {
    loading.value = false
  }
}

function googleLogin() {
  window.location.href = authService.getGoogleLoginUrl()
}
</script>

<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <div class="w-full max-w-md bg-white rounded-lg border border-gray-200 p-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">
        {{ isRegister ? 'Create Account' : 'Sign In' }}
      </h2>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
        {{ error }}
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="isRegister">
          <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            id="name"
            v-model="name"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            minlength="8"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In') }}
        </button>
      </form>

      <div class="mt-4">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">or</span>
          </div>
        </div>

        <button
          @click="googleLogin"
          class="mt-4 w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Continue with Google
        </button>
      </div>

      <p class="mt-6 text-center text-sm text-gray-600">
        <template v-if="isRegister">
          Already have an account?
          <button @click="isRegister = false" class="text-blue-600 hover:underline">Sign in</button>
        </template>
        <template v-else>
          Don't have an account?
          <button @click="isRegister = true" class="text-blue-600 hover:underline">Create one</button>
        </template>
      </p>
    </div>
  </div>
</template>
