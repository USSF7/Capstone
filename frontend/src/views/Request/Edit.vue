<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Edit Request</h1>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <fwb-input
          v-model="form.equipmentName"
          label="Equipment Name"
          placeholder="enter equipment name"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <label for="eventSelect" class="block text-sm font-medium text-gray-700 mb-1">
          Event
        </label>
        <select
          id="eventSelect"
          v-model.number="form.eventId"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">(no event)</option>
          <option value="" disabled>Select an event</option>
          <option v-for="e in events" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.location"
          label="Location"
          placeholder="enter location"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.startDate"
          label="Start Date"
          type="date"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.endDate"
          label="End Date"
          type="date"
          size="md"
          required
        />
      </div>


      <div class="mb-4">
        <fwb-input
          v-model.number="form.maxPrice"
          label="Max Price"
          type="number"
          :step="0.01"
          :min="0"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Comments
        </label>
        <textarea
          v-model="form.comments"
          placeholder="enter any additional comments"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          rows="4"
        ></textarea>
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? 'Submitting...' : 'Submit' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { FwbInput } from 'flowbite-vue'
import requestService from '../../services/requestService'
import eventService from '../../services/eventService'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')
const events = ref([])

const form = ref({
  equipmentName: '',
  countWanted: 1,
  eventId: '',
  location: '',
  startDate: '',
  endDate: '',
  minPrice: 0,
  maxPrice: 0,
  comments: ''
})

onMounted(async () => {
  try {
    // load available events for select box
    events.value = await eventService.getEvents()
  } catch (e) {
    console.error('Failed to fetch events', e)
  }

  // load the request itself
  const id = route.params.id
  if (id) {
    try {
      const req = await requestService.getRequest(id)
      form.value.equipmentName = req.name
      form.value.countWanted = req.count
      form.value.eventId = req.event_id || ''
      form.value.location = req.location
      // backend returns ISO strings, strip time portion for <input type=date>
      form.value.startDate = req.start_date.split('T')[0]
      form.value.endDate = req.end_date.split('T')[0]
      form.value.maxPrice = req.max_price
      form.value.minPrice = req.min_price ?? 0
      form.value.comments = req.comments ?? ''
    } catch (e) {
      error.value = 'Unable to load request for editing'
      console.error(e)
    }
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id
    const payload = {
      name: form.value.equipmentName,
      count: form.value.countWanted,
      event_id: form.value.eventId || null,
      location: form.value.location,
      start_date: form.value.startDate,
      end_date: form.value.endDate,
      max_price: form.value.maxPrice,
      min_price: form.value.minPrice,
      comments: form.value.comments
    }

    await requestService.updateRequest(id, payload)
    router.push({ name: 'requests' })
  } catch (err) {
    error.value = err.message || 'Failed to update request'
    console.error('Error updating request:', err)
  } finally {
    loading.value = false
  }
}
</script>
