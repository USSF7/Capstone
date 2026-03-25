<script setup>
import { onMounted, ref } from 'vue'
import userService from '../services/userService'

const users = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    users.value = await userService.getUsers()
  } catch (err) {
    error.value = err.message || 'Failed to load users'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Users</h1>

    <p v-if="loading" class="text-gray-600">Loading users...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <ul v-else class="space-y-3">
      <li
        v-for="user in users"
        :key="user.id"
        class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
      >
        <p class="font-semibold text-gray-900">{{ user.name }}</p>
        <p class="text-gray-600">{{ user.email }}</p>
      </li>
    </ul>
  </section>
</template>
