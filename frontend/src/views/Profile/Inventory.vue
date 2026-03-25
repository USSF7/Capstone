<!-- My Inventory View -->
<template>
  <section>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Inventory</h1>
    </div>

    <p v-if="loading" class="text-gray-600">Loading inventory...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <p v-else-if="equipment.length === 0" class="text-gray-600">No equipment in your inventory.</p>

    <div v-else class="grid grid-cols-1 gap-4">
      <fwb-card
        v-for="item in equipment"
        :key="item.id"
        class="w-sm"
      >
        <div class="p-5">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            {{ item.name }}
          </h5>

          <div v-if="item.active_rental" class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <span class="inline-block px-2 py-1 mb-2 text-xs font-semibold text-yellow-800 bg-yellow-200 rounded-full">
              Rented Out
            </span>
            <p><strong>Renter:</strong> {{ item.active_rental.renter_name }}</p>
            <p><strong>From:</strong> {{ formatDate(item.active_rental.start_date) }}</p>
            <p><strong>Until:</strong> {{ formatDate(item.active_rental.end_date) }}</p>
          </div>

          <div v-else class="mt-2">
            <span class="inline-block px-2 py-1 text-xs font-semibold text-green-800 bg-green-200 rounded-full">
              Available
            </span>
          </div>
        </div>
      </fwb-card>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { FwbCard } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import equipmentService from '../../services/equipmentService'

const auth = useAuthStore()
const userId = computed(() => auth.user?.id)

const equipment = ref([])
const loading = ref(true)
const error = ref('')

async function loadInventory() {
  try {
    equipment.value = await equipmentService.getEquipmentByOwnerWithRentals(userId.value)
  } catch (err) {
    error.value = err.message || 'Failed to load inventory'
  } finally {
    loading.value = false
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

onMounted(loadInventory)
</script>
