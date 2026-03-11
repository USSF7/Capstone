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

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          <button
            class="px-3 py-1.5 text-sm rounded-full bg-red-600 text-white font-medium hover:bg-red-700"
            @click="deleteEvent(event.id)"
          >
            Delete
          </button>
        </div>

        <div class="p-5 bg-gray-800 rounded-md text-white">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-white">
            {{ event.name }}
          </h5>
          <p class="text-sm"><strong>Start Date:</strong> {{ formatDate(event.start_date || event.date) }}</p>
          <p class="text-sm"><strong>End Date:</strong> {{ formatDate(event.end_date || event.date) }}</p>
        </div>
      </fwb-card>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { FwbCard, FwbButton } from 'flowbite-vue'
import eventService from '../../services/eventService'

const events = ref([])
const loading = ref(true)
const error = ref('')

async function loadEvents() {
  try {
    const data = await eventService.getEvents()
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
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(loadEvents)
</script>