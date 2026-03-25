<!-- View of all recommendations for the signed in user's profile -->
<script lang="js" setup>

import { onMounted, ref, computed } from 'vue'
import { FwbCard } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'

const auth = useAuthStore()
const userData = ref()
const loading = ref(true)
const error = ref('')

const userId = computed(() => auth.user?.id)

async function loadUser() {
    // Get the current user's data
    userData.value = await UserService.getUser(userId.value)
}

async function loadRecommendations() {
  userData.value.recommendations = []
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
    <p v-else-if="!userData?.recommendations?.length" class="text-gray-600">No recommendations yet.</p>

    <div v-else class="grid grid-cols-2 gap-4">
      <fwb-card
        v-for="request in userData.recommendations"
        :key="request.id"
        class="w-sm relative"
      >
        <div class="p-5">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            {{ request.name }}
          </h5>
          <p><strong>Date:</strong> {{ formatDate(request.start_date) }}</p>
        </div>
      </fwb-card>
    </div>
  </section>
</template>