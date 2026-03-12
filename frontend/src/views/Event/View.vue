<template>
  <section>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-6 max-w-md">
        <h2 class="text-2xl font-semibold mb-4">Event Details</h2>
        <div v-if="loading" class="text-gray-600">Loading...</div>
        <div v-else-if="error" class="text-red-600">{{ error }}</div>
        <div v-else>
          <p><strong>Name:</strong> {{ event.name }}</p>
          <p><strong>Date:</strong> {{ formatDate(event.date) }}</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <router-link :to="{ name: 'events-edit', params: { id: event.id } }">
              <button class="px-4 py-2 bg-yellow-600 text-white font-medium rounded-md hover:bg-yellow-700">
                Edit
              </button>
            </router-link>
            <button
              @click="deleteEvent"
              class="px-4 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700"
            >
              Delete
            </button>
            <router-link to="/events">
              <button class="px-4 py-2 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700">
                Back
              </button>
            </router-link>
          </div>
        </div>
      </div>

      <div class="lg:justify-self-end w-full max-w-md flex items-start justify-end">
        <router-link :to="{ name: 'requests-create' }">
          <button class="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700">
            Add Request
          </button>
        </router-link>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <p v-if="loadingRequests" class="text-gray-600">Loading requests...</p>
      <p v-else-if="requestsError" class="text-red-600">{{ requestsError }}</p>
      <div v-else-if="eventRequests.length === 0" class="text-gray-600">No requests found for this event.</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="req in eventRequests"
          :key="req.id"
          class="border border-gray-200 rounded-md p-3"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <p><strong>Request:</strong> {{ req.name }}</p>
              <p><strong>Max Price:</strong> {{ req.max_price }}</p>
              <p><strong>Count:</strong> {{ req.count }}</p>
              <p><strong>Start:</strong> {{ formatDate(req.start_date) }}</p>
              <p><strong>End:</strong> {{ formatDate(req.end_date) }}</p>
              <p><strong>Location:</strong> {{ req.location }}</p>
              <p><strong>Status:</strong> {{ req.status }}</p>
            </div>
            <div class="flex flex-col gap-2 shrink-0 self-start">
              <router-link class="block" :to="{ name: 'requests-view', params: { id: req.id } }">
                <button class="w-full px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700">
                  View
                </button>
              </router-link>
              <router-link class="block" :to="{ name: 'requests-edit', params: { id: req.id } }">
                <button class="w-full px-3 py-1.5 bg-yellow-500 text-white text-sm font-medium rounded-md hover:bg-yellow-600">
                  Edit
                </button>
              </router-link>
              <button
                @click="deleteRequest(req.id)"
                class="w-full px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import eventService from '../../services/eventService'
import requestService from '../../services/requestService'

const route = useRoute()
const router = useRouter()
const event = ref({})
const loading = ref(true)
const error = ref('')
const eventRequests = ref([])
const loadingRequests = ref(true)
const requestsError = ref('')

function formatDate(iso) {
  if (!iso) return '—'
  const [year, month, day] = iso.split('T')[0].split('-')
  const date = new Date(year, month - 1, day)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

async function deleteEvent() {
  if (confirm('Are you sure you want to delete this event?')) {
    try {
      await eventService.deleteEvent(event.value.id)
      router.push({ name: 'events' })
    } catch (e) {
      error.value = 'Failed to delete event'
      console.error(e)
    }
  }
}

async function deleteRequest(requestId) {
  if (confirm('Are you sure you want to delete this request?')) {
    try {
      await requestService.deleteRequest(requestId)
      eventRequests.value = eventRequests.value.filter(req => req.id !== requestId)
    } catch (e) {
      requestsError.value = 'Failed to delete request'
      console.error(e)
    }
  }
}

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'No event id provided'
    loading.value = false
    return
  }

  try {
    const ev = await eventService.getEvent(id)
    event.value = ev

    try {
      eventRequests.value = await requestService.getRequestsByEvent(id)
    } catch (reqErr) {
      requestsError.value = reqErr.message || 'Failed to load event requests'
      console.error(reqErr)
    } finally {
      loadingRequests.value = false
    }
  } catch (e) {
    error.value = 'Failed to load event'
    console.error(e)
    loadingRequests.value = false
  } finally {
    loading.value = false
  }
})
</script>
