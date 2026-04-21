<script setup>
/**
 * Functions for managing the meeting location picker on the Google Maps
 * @module MeetingLocationPicker
 */

import { ref, onMounted } from 'vue'
import { FwbButton, FwbCard, FwbSpinner } from 'flowbite-vue'
import locationService from '../services/locationService'

/**
 * Suggested meeting place.
 * @typedef {Object} MeetingPlace
 * @property {string} name - Name of the place.
 * @property {string} address - Address of the place.
 * @property {number} lat - Latitude coordinate value of the place.
 * @property {number} lng - Longitude coordinate value of the place.
 * @property {string} place_id - The place ID.
 * @property {string} place_type - The place type.
 */

/**
 * Basic user and location information returned by the API.
 * @typedef {Object} ParticipantInfo
 * @property {number} id - Participant ID number.
 * @property {string} [name] - Name of the participant.
 * @property {{ lat: number, lng: number }} [location] - Latitude and Longitude coordinate values.
 */

/**
 * API response for meeting suggestions.
 * @typedef {Object} MeetingSuggestionsResponse
 * @property {{ lat: number, lng: number }} midpoint - Latitude and Longitude coordinate values of the suggested meeting point.
 * @property {MeetingPlace[]} suggestions - Suggested meeting places.
 * @property {ParticipantInfo} renter - The renter information.
 * @property {ParticipantInfo} vendor - The vendor information.
 */

/**
 * Component props.
 * @typedef {Object} Props
 * @property {number|string} rentalId - Rental ID used to fetch suggestions.
 */

/** @type {Props} */
const props = defineProps({
  rentalId: { type: [Number, String], required: true },
})

/**
 * Emits events from the location-selected component.
 *
 * @type {(event: 'location-selected', payload: { place: MeetingPlace, rental: any }) => void}
 */
const emit = defineEmits(['location-selected'])

/**
 * Loading state while fetching suggestions.
 * @type {import('vue').Ref<boolean>}
 */
const loading = ref(true)

/**
 * Error message if API call fails.
 * @type {import('vue').Ref<string|null>}
 */
const error = ref(null)

/**
 * Midpoint location between renter and vendor.
 * @type {import('vue').Ref<{ lat: number, lng: number } | null>}
 */
const midpoint = ref(null)

/**
 * List of suggested meeting locations.
 * @type {import('vue').Ref<MeetingPlace[]>}
 */
const suggestions = ref([])

/**
 * Renter information.
 * @type {import('vue').Ref<ParticipantInfo|null>}
 */
const renterInfo = ref(null)

/**
 * Vendor information.
 * @type {import('vue').Ref<ParticipantInfo|null>}
 */
const vendorInfo = ref(null)

/**
 * Indicates location selection is in progress. Disables user interface interactions while submitting.
 * @type {import('vue').Ref<boolean>}
 */
const selecting = ref(false)

/**
 * Maps place types to human-readable labels. Used for display in the user interface.
 */
const placeTypeLabels = {
  library: 'Library',
  park: 'Park',
  police: 'Police Station',
  fire_station: 'Fire Station',
  post_office: 'Post Office',
}

/**
 * Fetches suggested meeting locations based on rental ID. Populates midpoint, suggestions, and participant information.
 */
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

/**
 * Selects a meeting location and persists it via API. Emits `location-selected` on success.
 *
 * @param {MeetingPlace} place
 */
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

/**
 * Load suggestions when the component mounts.
 */
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
