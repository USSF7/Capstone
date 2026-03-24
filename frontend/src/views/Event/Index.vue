<!-- View for person to see all of their events -->
<template>
  <section>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Events</h1>
      <router-link
        to="/events/create"
        class="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
      >
        Create New Event
      </router-link>
    </div>

    <p v-if="loading" class="text-gray-600">Loading events...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <p v-else-if="events.length === 0" class="text-gray-600">No events found for your account.</p>

    <div v-else class="grid grid-cols-1 gap-4">
      <fwb-card
        v-for="event in events"
        :key="event.id"
        class="w-sm relative"
      >
        <!-- action buttons top-right -->
        <div class="absolute top-2 right-2 flex gap-2">
          <router-link :to="{ name: 'events-view', params: { id: event.id } }">
            <fwb-button color="Green" pill>View</fwb-button>
          </router-link>
          <router-link :to="{ name: 'events-edit', params: { id: event.id } }">
            <fwb-button color="Yellow" pill>Edit</fwb-button>
          </router-link>
          <fwb-button color="Red" pill @click="deleteEvent(event.id)">Delete</fwb-button>
        </div>

        <div class="p-5">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            {{ event.name }}
          </h5>
          <p><strong>Date:</strong> {{ formatDate(event.date) }}</p>
        </div>
      </fwb-card>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { FwbCard, FwbButton } from 'flowbite-vue'
import eventService from '../../services/eventService'
import authService from '../../services/authService'

const events = ref([])
const loading = ref(true)
const error = ref('')
const auth = useAuthStore()

async function ensureCurrentUser() {
  if (auth.user?.id) return auth.user
  if (!auth.accessToken) return null

  try {
    const me = await authService.getMe()
    auth.setAuth({
      access_token: auth.accessToken,
      refresh_token: auth.refreshToken,
      user: me
    })
    return me
  } catch {
    return null
  }
}

async function loadEvents() {
  try {
    const currentUser = await ensureCurrentUser()
    const userId = currentUser?.id || auth.user?.id

    if (!userId) {
      events.value = []
      error.value = 'You must be logged in to view your events.'
      return
    }

    const data = await eventService.getEventsByUser(userId)
    events.value = data
  } catch (err) {
    error.value = err.message || 'Failed to load events'
  } finally {
    loading.value = false
  }
}

async function deleteEvent(eventId) {
  if (confirm('Are you sure you want to delete this event?')) {
    try {
      await eventService.deleteEvent(eventId)
      // Remove the deleted event from the list
      events.value = events.value.filter(e => e.id !== eventId)
    } catch (err) {
      error.value = err.message || 'Failed to delete event'
    }
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const [year, month, day] = dateString.split('T')[0].split('-')
  const date = new Date(year, month - 1, day)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(loadEvents)
</script>