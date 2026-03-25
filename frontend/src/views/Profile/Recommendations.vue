<!-- View of all recommendations for the signed in user's profile -->
<script lang="js" setup>

import { onMounted, ref, computed } from 'vue'
import { FwbCard, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import RequestService from '../../services/requestService'
import UserService from '../../services/userService'

const auth = useAuthStore()
const userData = ref()
const loading = ref(true)

const userId = computed(() => auth.user?.id)

async function loadUser() {
    // Get the current user's data
    userData.value = await UserService.getUser(userId.value)
}

async function loadRecommendations() {
    // Get the current user's recommendations data
    userData.value.recommendations = await RequestService.getRecommendationsByRenter(userId.value)
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(async () => {
    // Validating the user's vendor status
    await loadUser()
    await loadRecommendations()

    loading.value = false
})
</script>

<template>
  <section>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Recommendations</h1>
    </div>

    <p v-if="loading" class="text-gray-600">Loading recommendations...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="grid grid-cols-2 gap-4">
      <fwb-card
        v-for="request in userData.recommendations"
        :key="request.id"
        class="w-sm relative"
      >
        <!-- action buttons top-right -->
        <div class="absolute top-2 right-2 flex gap-2">
          <router-link :to="{ name: 'requests-view', params: { id: request.id } }">
            <fwb-button color="Green" pill>View</fwb-button>
          </router-link>
        </div>

        <div class="p-5">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            Equipment name: {{ request.name }}
          </h5>
          <p><strong>Event Name:</strong> {{ request.event_name }}</p>
          <p><strong>Max Price:</strong> {{ request.max_price }}</p>
          <p><strong>Count:</strong> {{ request.count }}</p>
          <p><strong>Start:</strong> {{ formatDate(request.start_date) }}</p>
          <p><strong>End:</strong> {{ formatDate(request.end_date) }}</p>
          <p><strong>Location:</strong> {{ request.location }}</p>
          <p><strong>Comments:</strong> {{ request.comments }}</p>
          <p><strong>Status:</strong> {{ request.status }}</p>
        </div>
      </fwb-card>
    </div>
  </section>
</template>