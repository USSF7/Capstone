<script setup>
import { onMounted, ref } from 'vue'
import requestService from '../services/requestService'

const requests = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    requests.value = await requestService.getRequests()
  } catch (err) {
    error.value = err.message || 'Failed to load requests'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Requests</h1>

    <p v-if="loading" class="text-gray-600">Loading request...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <ul v-else class="space-y-3">
      <li
        v-for="request in requests"
        :key="request.id"
        class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
      >
        <p class="font-semibold text-gray-900">{{ request.name }}</p>
        <p class="text-gray-600">{{ request.location }}</p>
      </li>
    </ul>
  </section>
</template>
