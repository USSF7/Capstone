<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Create New Event</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <fwb-input
          v-model="form.eventName"
          label="Event Name"
          placeholder="enter event name"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
        <input
          v-model="form.date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
import eventService from '../../services/eventService'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = ref({
  eventName: '',
  date: '',
  comments: ''
})

onMounted(async () => {
  // Events loading removed
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await eventService.createEvent(
      1, // user_id placeholder
      form.value.eventName,
      form.value.date
    )
    console.log('Event created:', response)
    router.push({ name: 'home' })
  } catch (err) {
    error.value = err.message || 'Failed to create event'
    console.error('Error creating event:', err)
  } finally {
    loading.value = false
  }
}
</script>