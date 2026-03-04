<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Create New Request</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

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
import { useRouter } from 'vue-router'
import { FwbInput } from 'flowbite-vue'
import requestService from '../../services/requestService'
import eventService from '../../services/eventService'

const router = useRouter()
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
  maxPrice: 0,
  comments: ''
})

onMounted(async () => {
  try {
    events.value = await eventService.getEvents()
  } catch (e) {
    console.error('Failed to fetch events', e)
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await requestService.createRequest(
      1, // requester_id placeholder
      form.value.eventId || null,
      form.value.equipmentName,
      form.value.maxPrice,
      form.value.countWanted,
      form.value.startDate,
      form.value.endDate,
      form.value.location,
      null, // minPrice
      form.value.comments
    )
    console.log('Request created:', response)
    router.push({ name: 'requests' })
  } catch (err) {
    error.value = err.message || 'Failed to create request'
    console.error('Error creating request:', err)
  } finally {
    loading.value = false
  }
}
</script>