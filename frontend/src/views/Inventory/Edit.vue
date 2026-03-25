<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Edit Equipment</h1>

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
        {{ loading ? 'Saving...' : 'Save Changes' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { FwbInput } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import equipmentService from '../../services/equipmentService'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')
const OWNER_ID = computed(() => auth.user?.id)

const form = ref({
  equipmentName: ''
})

onMounted(async () => {
  const id = route.params.id
  if (id) {
    try {
      const equipment = await equipmentService.getEquipmentById(id)
      form.value.equipmentName = equipment.name
    } catch (e) {
      error.value = 'Unable to load equipment for editing'
      console.error(e)
    }
  } else {
    error.value = 'Missing equipment id'
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id

    if (!id) {
      throw new Error('Missing equipment id')
    }

    await equipmentService.updateEquipment(
      id,
      form.value.equipmentName,
      OWNER_ID.value
    )

    router.push({ name: 'inventory' })
  } catch (err) {
    error.value = err.message || 'Failed to update equipment'
    console.error('Error updating equipment:', err)
  } finally {
    loading.value = false
  }
}
</script>
