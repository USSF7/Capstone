<script setup>
/**
 * Equipment search functions
 * @module EquipmentSearch
 */

import { ref, computed, onMounted } from 'vue'
import { FwbButton, FwbInput, FwbSpinner } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import locationService from '../../services/locationService'
import GoogleMap from '../../components/GoogleMap.vue'
import EquipmentResultsGrid from '../../components/EquipmentResultsGrid.vue'

/**
 * Auth store containing user location data.
 */
const auth = useAuthStore()

/**
 * Backend base URL for serving images.
 * @type {string}
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

/**
 * Equipment name input for searching for specific equipment.
 */
const nameFilter = ref('')

/**
 * Search radius from the user's location.
 */
const radius = ref(25)

/**
 * Search results from the filter name and radius.
 * @type {import('vue').Ref<Array<any>>}
 */
const results = ref([])

/**
 * User interface loading flag.
 */
const loading = ref(false)

/**
 * User interface error flag.
 */
const error = ref(null)

/**
 * User interface display map flag.
 */
const showMap = ref(false)

/**
 * User interface equipment searched flag.
 */
const searched = ref(false)

/**
 * User latitude coordinate derived from auth store.
 */
const userLat = computed(() => auth.user?.latitude)

/**
 * User longitude coordinate derived from auth store.
 */
const userLng = computed(() => auth.user?.longitude)

/**
 * Whether the user has a valid location set.
 */
const hasLocation = computed(() => userLat.value != null && userLng.value != null)

/**
 * Escapes HTML to prevent XSS in map info windows.
 *
 * @param {string} value
 * @returns {string} A user interface payload.
 */
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

/**
 * Builds HTML content for a map marker info window.
 *
 * @param {any} item - The equipment object.
 * @returns {string} HTML string for Google Maps InfoWindow
 */
function buildMapLabel(item) {
  const safeName = escapeHtml(item.name)
  const detailsUrl = `/equipment/${item.id}/view`
  const hasPicture = !!item.picture
  const pictureSrc = hasPicture ? `${BACKEND_URL}/${item.picture}` : ''

  return `
    <div style="display:flex;gap:10px;align-items:flex-start;max-width:250px;">
      ${hasPicture
        ? `<img src="${pictureSrc}" alt="${safeName}" style="width:52px;height:52px;object-fit:cover;border-radius:6px;border:1px solid #e5e7eb;" />`
        : `<div style="width:52px;height:52px;border-radius:6px;border:1px solid #e5e7eb;background:#f3f4f6;"></div>`}
      <div>
        <div style="font-weight:600;color:#111827;line-height:1.2;">${safeName}</div>
        <div style="font-size:12px;color:#374151;">$${item.price}/day</div>
        <div style="font-size:12px;color:#6b7280;">${item.distance_miles} mi away</div>
        <a href="${detailsUrl}" style="display:inline-block;margin-top:6px;font-size:12px;color:#2563eb;text-decoration:underline;">View equipment</a>
      </div>
    </div>
  `
}

/**
 * Transforms search results into map marker objects.
 */
const mapMarkers = computed(() =>
  results.value.map((r) => ({
    lat: r.owner_lat,
    lng: r.owner_lng,
    title: r.name,
    label: buildMapLabel(r),
  }))
)

/**
 * Equipment search result item.
 * @typedef {Object} EquipmentResult
 * @property {number} id - The equipment ID number.
 * @property {string} name - The equipment name.
 * @property {number} price - The price of the equipment.
 * @property {number} distance_miles - The distance from the renter's location to the vendor's location.
 * @property {string} [picture] - Picture of the equipment.
 * @property {number} owner_lat - The latitude coordinate value of the vendor.
 * @property {number} owner_lng - The longitude coordinate value of the vendor.
 */

/**
 * Executes a search for nearby equipment.
 */
async function search() {
  if (!hasLocation.value) return
  loading.value = true
  error.value = null
  searched.value = true
  try {
    const data = await locationService.searchEquipmentNearby(
      userLat.value,
      userLng.value,
      radius.value,
      nameFilter.value || null
    )
    results.value = data.results
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

/**
 * Automatically runs an initial search on mount if the user has a location set.
 */
onMounted(() => {
  if (hasLocation.value) search()
})
</script>

<template>
  <section class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Find Equipment Near You</h1>

    <div v-if="!hasLocation" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <p class="text-yellow-800">
        Your location is not set. Please
        <router-link to="/profile/edit" class="underline font-medium">update your profile address</router-link>
        to search for nearby equipment.
      </p>
    </div>

    <form v-else @submit.prevent="search" class="flex flex-wrap items-end gap-4 mb-6">
      <div class="flex-1 min-w-[200px]">
        <label class="block text-sm font-medium text-gray-700 mb-1">Equipment Name</label>
        <fwb-input v-model="nameFilter" placeholder="e.g. Spikeball, Mountain Bike" />
      </div>
      <div class="w-32">
        <label class="block text-sm font-medium text-gray-700 mb-1">Radius (miles)</label>
        <fwb-input v-model="radius" type="number" min="1" max="500" />
      </div>
      <fwb-button type="submit" :disabled="loading">
        {{ loading ? 'Searching...' : 'Search' }}
      </fwb-button>
    </form>

    <div v-if="loading" class="flex justify-center py-8">
      <fwb-spinner size="10" />
    </div>

    <p v-if="error" class="text-red-600 text-sm mb-4">{{ error }}</p>

    <div v-if="!loading && results.length">
      <div class="flex items-center justify-between mb-4">
        <p class="text-sm text-gray-600">{{ results.length }} item{{ results.length !== 1 ? 's' : '' }} found</p>
        <fwb-button size="sm" color="light" @click="showMap = !showMap">
          {{ showMap ? 'Hide Map' : 'Show on Map' }}
        </fwb-button>
      </div>

      <GoogleMap
        v-if="showMap"
        :center="{ lat: userLat, lng: userLng }"
        :zoom="11"
        :markers="mapMarkers"
        height="350px"
        class="mb-6"
      />

      <EquipmentResultsGrid :items="results" />
    </div>

    <p v-if="!loading && searched && !results.length && !error" class="text-gray-500 text-center py-8">
      No equipment found within {{ radius }} miles. Try increasing the search radius.
    </p>
  </section>
</template>
