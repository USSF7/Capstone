<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Create New Request</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <label for="equipmentName" class="block text-sm font-medium text-gray-700 mb-1">Equipment Name</label>
        <select
          id="equipmentName"
          v-model="form.equipmentName"
          size="8"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 max-h-48 overflow-y-auto"
          required
        >
          <option value="">Select equipment...</option>
          <option v-for="name in equipmentNames" :key="name" :value="name">{{ name }}</option>
        </select>
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
          label="Location (Street, City, State ZIP)"
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
          v-model.number="form.countWanted"
          label="Count"
          type="number"
          :min="1"
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
      
      <div v-if="averagePriceInfo" class="mb-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p class="text-sm text-blue-800">{{ averagePriceInfo }}</p>
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
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FwbInput } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import requestService from '../../services/requestService'
import eventService from '../../services/eventService'
import equipmentService from '../../services/equipmentService'
import rentalService from '../../services/rentalService'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const events = ref([])
const equipmentNames = ref([])
const averagePriceInfo = ref('')

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

const loadEquipmentNames = async () => {
  try {
    const response = await equipmentService.getEquipmentNames()
    if (response && response.equipment_names) {
      equipmentNames.value = response.equipment_names
    }
  } catch (e) {
    console.error('Failed to fetch equipment names', e)
  }
}

onMounted(async () => {
  try {
    events.value = await eventService.getEvents()
    await loadEquipmentNames()
    if (auth.user?.street_address) {
      form.value.location = auth.user.street_address
    }
  } catch (e) {
    console.error('Failed to fetch initialization data', e)
  }
})

// Watch for changes in equipment name and location to fetch average price
watch([() => form.value.equipmentName, () => form.value.location], async ([newEquipmentName, newLocation]) => {
  if (newEquipmentName && newLocation) {
    try {
      const response = await rentalService.getAveragePrice(newEquipmentName, newLocation)
      if (response && response.average_price !== null) {
        // Parse city and state from location
        const cityState = parseCityState(newLocation)
        if (cityState) {
          averagePriceInfo.value = `The average price of ${newEquipmentName} in ${cityState} is $${response.average_price.toFixed(2)}`
        } else {
          averagePriceInfo.value = `The average why price of ${newEquipmentName} is $${response.average_price.toFixed(2)}`
        }
      } else {
        averagePriceInfo.value = ''
      }
    } catch (e) {
      console.error('Failed to fetch average price', e)
      averagePriceInfo.value = ''
    }
  } else {
    averagePriceInfo.value = ''
  }
})

const parseCityState = (location) => {
  // Parse city and state from location string
  // Expected format: "Street Address, City, State ZIP"
  const parts = location.split(',').map(part => part.trim())
  if (parts.length >= 3) {
    const city = parts[parts.length - 2]
    const stateZip = parts[parts.length - 1].split(' ')
    if (stateZip.length >= 1) {
      const state = stateZip[0]
      return `${city}, ${state}`
    }
  }
  return null
}

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    if (!auth.user?.id) {
      throw new Error('You must be logged in to create a request')
    }

    const response = await requestService.createRequest(
      auth.user.id,
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