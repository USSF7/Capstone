<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Edit Event</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <fwb-input
          v-model="form.name"
          label="Event Name"
          placeholder="enter event name"
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
import eventService from '../../services/eventService'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')

const form = ref({
  name: '',
  startDate: '',
  endDate: '',
  comments: ''
})

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'No event ID provided'
    return
  }

  try {
    const ev = await eventService.getEvent(id)
    form.value.name = ev.name
    // backend returns ISO strings, strip time portion for <input type=date>
    form.value.startDate = ev.date.split('T')[0]
    // Backend currently supports a single event date, so default end date to start date.
    form.value.endDate = ev.date.split('T')[0]
  } catch (e) {
    error.value = 'Unable to load event for editing'
    console.error(e)
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id
    await eventService.updateEvent(id, form.value.name, form.value.startDate)
    router.push({ name: 'events' })
  } catch (err) {
    error.value = err.message || 'Failed to update event'
    console.error('Error updating event:', err)
  } finally {
    loading.value = false
  }
}
</script>