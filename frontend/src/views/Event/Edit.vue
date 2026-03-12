<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Edit Event</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>
    <p v-if="success" class="text-green-600 mb-4">Event updated successfully!</p>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
        <input
          v-model="form.name"
          type="text"
          placeholder="enter event name"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
import { useRouter, useRoute } from 'vue-router'
import eventService from '../../services/eventService'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')
const success = ref(false)

const form = ref({
  name: '',
  date: '',
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
    form.value.date = ev.date ? ev.date.split('T')[0] : ''
  } catch (e) {
    error.value = 'Unable to load event for editing'
    console.error(e)
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  const id = route.params.id
  try {
    const result = await eventService.updateEvent(id, form.value.name, form.value.date)
    success.value = true
    setTimeout(() => router.push({ name: 'events' }), 800)
  } catch (err) {
    error.value = err.message || 'Failed to update event'
    console.error('Error updating event:', err)
  } finally {
    loading.value = false
  }
}
</script>