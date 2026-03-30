<script setup>
import { ref, onMounted } from 'vue'
import { FwbButton, FwbCard, FwbSpinner } from 'flowbite-vue'
import locationService from '../services/locationService'

const props = defineProps({
  rentalId: { type: [Number, String], required: true },
})

const emit = defineEmits(['location-selected'])

const loading = ref(true)
const error = ref(null)
const midpoint = ref(null)
const suggestions = ref([])
const renterInfo = ref(null)
const vendorInfo = ref(null)
const selecting = ref(false)

const placeTypeLabels = {
  library: 'Library',
  park: 'Park',
  police: 'Police Station',
  fire_station: 'Fire Station',
  post_office: 'Post Office',
}

async function loadSuggestions() {
  try {
    const data = await locationService.getMeetingSuggestions(props.rentalId)
    midpoint.value = data.midpoint
    suggestions.value = data.suggestions
    renterInfo.value = data.renter
    vendorInfo.value = data.vendor
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function selectLocation(place) {
  selecting.value = true
  try {
    const updated = await locationService.setMeetingLocation(props.rentalId, {
      name: place.name,
      address: place.address,
      lat: place.lat,
      lng: place.lng,
      place_id: place.place_id,
    })
    emit('location-selected', { place, rental: updated })
  } catch (e) {
    error.value = e.message
  } finally {
    selecting.value = false
  }
}

onMounted(loadSuggestions)
</script>

<template>
  <div>
    <h3 class="text-lg font-semibold text-gray-800 mb-4">Suggested Meeting Locations</h3>

    <div v-if="loading" class="flex items-center gap-2 text-gray-500">
      <fwb-spinner size="6" />
      <span>Finding safe meeting locations...</span>
    </div>

    <p v-if="error" class="text-red-600 text-sm mb-4">{{ error }}</p>

    <div v-if="!loading && suggestions.length" class="space-y-3">
      <fwb-card v-for="place in suggestions" :key="place.place_id" class="p-4">
        <div class="flex justify-between items-center">
          <div>
            <h4 class="font-medium text-gray-900">{{ place.name }}</h4>
            <p class="text-sm text-gray-500">{{ place.address }}</p>
            <span class="inline-block mt-1 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
              {{ placeTypeLabels[place.place_type] || place.place_type }}
            </span>
          </div>
          <fwb-button size="sm" @click="selectLocation(place)" :disabled="selecting">
            Select
          </fwb-button>
        </div>
      </fwb-card>
    </div>

    <p v-if="!loading && !error && !suggestions.length" class="text-gray-500">
      No public meeting locations found near the midpoint. Try adjusting the search area.
    </p>
  </div>
</template>
