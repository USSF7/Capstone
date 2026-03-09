<!-- My Requests View -->
<template>
  <section>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Requests</h1>
      <router-link
        to="/requests/create"
        class="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
      >
        Make New Request
      </router-link>
    </div>

    <p v-if="loading" class="text-gray-600">Loading requests...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="grid grid-cols-1 gap-4">
      <fwb-card
        v-for="request in requests"
        :key="request.id"
        class="w-sm relative"
      >
        <!-- action buttons top-right -->
        <div class="absolute top-2 right-2 flex gap-2">
          <router-link :to="{ name: 'requests-view', params: { id: request.id } }">
            <fwb-button color="Green" pill>View</fwb-button>
          </router-link>
          <router-link :to="{ name: 'requests-edit', params: { id: request.id } }">
            <fwb-button color="Yellow" pill>Edit</fwb-button>
          </router-link>
          <fwb-button color="Red" pill @click="deleteRequest(request.id)">Delete</fwb-button>
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

<script setup>
import { onMounted, ref } from 'vue'
import { FwbCard, FwbButton } from 'flowbite-vue'
import requestService from '../../services/requestService'
import eventService from '../../services/eventService'

const requests = ref([])
const loading = ref(true)
const error = ref('')

async function loadRequestsWithEventNames() {
  try {
    // initial list of requests
    const data = await requestService.getRequests()
    // for each request fetch the related event
    const enhanced = await Promise.all(
      data.map(async (r) => {
        let eventName = null
        if (r.event_id) {
          try {
            const eventObj = await eventService.getEvent(r.event_id)
            eventName = eventObj.name
          } catch (e) {
            console.warn('failed to load event', r.event_id, e)
          }
        }
        return { ...r, event_name: eventName }
      })
    )
    requests.value = enhanced
  } catch (err) {
    error.value = err.message || 'Failed to load requests'
  } finally {
    loading.value = false
  }
}

async function deleteRequest(requestId) {
  if (confirm('Are you sure you want to delete this request?')) {
    try {
      await requestService.deleteRequest(requestId)
      // Remove the deleted request from the list
      requests.value = requests.value.filter(r => r.id !== requestId)
    } catch (err) {
      error.value = err.message || 'Failed to delete request'
    }
  }
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

onMounted(loadRequestsWithEventNames)
</script>