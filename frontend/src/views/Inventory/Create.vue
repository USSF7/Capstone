<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Add Equipment</h1>

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

      <button
        type="submit"
        :disabled="loading"
        class="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? 'Creating...' : 'Create Equipment' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { FwbInput } from 'flowbite-vue'
import equipmentService from '../../services/equipmentService'

// TODO: Replace with authenticated user id when auth module is integrated.
const OWNER_ID = 10

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = ref({
  equipmentName: ''
})

const submitForm = async () => {
  loading.value = true
  error.value = ''

  try {
    await equipmentService.createEquipment(OWNER_ID, form.value.equipmentName)
    router.push({ name: 'inventory' })
  } catch (err) {
    error.value = err.message || 'Failed to create equipment'
    console.error('Error creating equipment:', err)
  } finally {
    loading.value = false
  }
}
</script>
