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

      <div class="mb-4">
        <fwb-input
          v-model.number="form.price"
          label="Price"
          type="number"
          :step="0.01"
          :min="0"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <fwb-select
          v-model="form.condition"
          :options="conditions"
          label="Condition"
          size="md"
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.description"
          label="Description"
          placeholder="enter equipment description"
          size="md"
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.picture"
          label="Picture Path"
          placeholder="/images/equipment/item.jpg"
          size="md"
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { FwbInput, FwbSelect } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import equipmentService from '../../services/equipmentService'

const conditions = [
  { value: 'Mint', name: '🔵 Mint' },
  { value: 'Above Average', name: '🟢 Above Average' },
  { value: 'Average', name: '🟡 Average' },
  { value: 'Below Average', name: '🔴 Below Average' }
]

const auth = useAuthStore()
const OWNER_ID = computed(() => auth.user?.id)

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = ref({
  equipmentName: '',
  price: 0,
  condition: '',
  description: '',
  picture: '',
})

const submitForm = async () => {
  loading.value = true
  error.value = ''

  try {
    await equipmentService.createEquipment(
      OWNER_ID.value,
      form.value.equipmentName,
      form.value.price,
      form.value.description,
      form.value.picture,
      form.value.condition
    )
    router.push({ name: 'inventory' })
  } catch (err) {
    error.value = err.message || 'Failed to create equipment'
    console.error('Error creating equipment:', err)
  } finally {
    loading.value = false
  }
}
</script>
