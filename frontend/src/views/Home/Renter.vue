<script setup>
/**
 * Home page for the renter view
 * @module HomeRenter 
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbSpinner, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import RentalService from '../../services/rentalService'
import LocationService from '../../services/locationService'
import EquipmentResultsGrid from '../../components/EquipmentResultsGrid.vue'

/**
 * Auth store containing current user and location data.
 */
const auth = useAuthStore()

/**
 * Router instance for navigation actions.
 */
const router = useRouter()

/**
 * List of all rentals for the current user.
 * @type {import('vue').Ref<Array<any>>}
 */
const rentals = ref([])

/**
 * Nearby equipment search results.
 * @type {import('vue').Ref<Array<any>>}
 */
const nearbyEquipment = ref([])

/**
 * Rental loading state for async data sources.
 */
const rentalsLoading = ref(true)

/**
 * Equipment loading state for async data sources.
 */
const equipmentLoading = ref(true)

/**
 * Rentals error state for async data sources.
 */
const rentalsError = ref(null)

/**
 * Equipment error state for async data sources.
 */
const equipmentError = ref(null)

/**
 * Getting all of the active rentals derived from all the rentals.
 */
const activeRentals = computed(() =>
  rentals.value
    .filter(r => !r.deleted && ['requesting', 'active'].includes(r.status))
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

/**
 * Checks if rental has not started yet.
 *
 * @param {any} rental - The rental data object.
 * @returns {boolean} Returns true if rental has not started yet. Otherwise, returns false.
 */
function isBeforeRentalStart(rental) {
  const now = Date.now()
  return now < new Date(rental.start_date).getTime()
}

/**
 * Checks if current time is within rental period.
 *
 * @param {any} rental - The rental data object.
 * @returns {boolean} Returns true if current time is within rental period. Otherwise, returns false.
 */
function isDuringRentalWindow(rental) {
  const now = Date.now()
  const start = new Date(rental.start_date).getTime()
  const end = new Date(rental.end_date).getTime()
  return now >= start && now <= end
}

/**
 * Maps rental status to progress bar percentage.
 */
const statusPercent = { requesting: 10, active: 70 }

/**
 * Maps rental status to progress bar color.
 */
const statusColor = { requesting: 'yellow', active: 'green' }

/**
 * Whether the user has a valid saved location.
 */
const hasLocation = computed(() => auth.user?.latitude != null && auth.user?.longitude != null)

/**
 * Formats ISO date into human-readable string.
 *
 * @param {string} iso - The date formatted in ISO format.
 * @returns {string} Human-readable formatted date string.
 */
function formatDate(iso) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/**
 * Loads rentals for the authenticated user. Populates active and historical rental data.
 */
async function loadRentals() {
  rentalsLoading.value = true
  rentalsError.value = null
  try {
    rentals.value = await RentalService.getRentalsWithEquipmentByRenter(auth.user.id)
  } catch (e) {
    rentalsError.value = e.message || 'Failed to load rentals.'
  } finally {
    rentalsLoading.value = false
  }
}

/**
 * Loads nearby equipment based on user location.
 */
async function loadNearbyEquipment() {
  if (!hasLocation.value) {
    equipmentLoading.value = false
    return
  }
  equipmentLoading.value = true
  equipmentError.value = null
  try {
    const data = await LocationService.searchEquipmentNearby(auth.user.latitude, auth.user.longitude, 25)
    nearbyEquipment.value = (data.results || []).slice(0, 6)
  } catch (e) {
    equipmentError.value = e.message || 'Failed to load nearby equipment.'
  } finally {
    equipmentLoading.value = false
  }
}

/**
 * Initial data fetch on component mount.
 */
onMounted(() => {
  loadRentals()
  loadNearbyEquipment()
})
</script>

<template>
  <section class="max-w-5xl mx-auto space-y-10">
    <!-- Welcome -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-2xl p-8 text-white">
      <h1 class="text-3xl font-bold">Welcome back, {{ auth.user?.name?.split(' ')[0] }}</h1>
      <p class="mt-2 text-grey-200">Here's what's happening with your rentals.</p>
    </div>

    <!-- Active Requests -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-800">Your Active Requests</h2>
        <fwb-button size="sm" color="light" @click="router.push({ name: 'rentals' })">
          View All Rentals
        </fwb-button>
      </div>

      <div v-if="rentalsLoading" class="flex justify-center py-8">
        <fwb-spinner size="10" />
      </div>

      <p v-else-if="rentalsError" class="text-red-600 text-sm">{{ rentalsError }}</p>

      <div v-else-if="activeRentals.length" class="space-y-4">
        <router-link
          v-for="rental in activeRentals"
          :key="rental.id"
          :to="{ name: 'rental_view', params: { id: rental.id } }"
          class="block !max-w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
        >
          <fwb-card class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow">
            <div class="flex flex-col p-5 gap-4">
              <div class="flex gap-5 items-start">
                <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-900 truncate">
                    {{ rental.equipment?.length ? rental.equipment.map(e => e.name).join(', ') : 'Equipment request' }}
                  </h3>
                  <p class="text-sm text-gray-500 mt-1">
                    {{ formatDate(rental.start_date) }} — {{ formatDate(rental.end_date) }}
                  </p>
                </div>
                <span class="text-lg font-bold text-blue-600 flex-shrink-0">${{ rental.agreed_price }}</span>
              </div>
              <fwb-progress
                :progress="statusPercent[rental.status]"
                :color="statusColor[rental.status]"
                size="md"
                :label="rental.status_text"
              />
            </div>
          </fwb-card>
        </router-link>
      </div>

      <div v-else class="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
        <p class="text-gray-500">No active requests right now.</p>
        <fwb-button size="sm" class="mt-3" @click="router.push({ name: 'equipment-search' })">
          Browse Equipment
        </fwb-button>
      </div>
    </div>

    <!-- Suggested Equipment Nearby -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-800">Suggested Equipment Nearby</h2>
        <fwb-button size="sm" color="light" @click="router.push({ name: 'equipment-search' })">
          Search All
        </fwb-button>
      </div>

      <div v-if="!hasLocation" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p class="text-yellow-800 text-sm">
          Your location is not set.
          <router-link to="/profile/edit" class="underline font-medium">Update your profile address</router-link>
          to see nearby equipment.
        </p>
      </div>

      <div v-else-if="equipmentLoading" class="flex justify-center py-8">
        <fwb-spinner size="10" />
      </div>

      <p v-else-if="equipmentError" class="text-red-600 text-sm">{{ equipmentError }}</p>

      <EquipmentResultsGrid
        v-else-if="nearbyEquipment.length"
        :items="nearbyEquipment"
      />

      <div v-else class="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
        <p class="text-gray-500">No equipment found nearby. Try expanding your search.</p>
        <fwb-button size="sm" class="mt-3" @click="router.push({ name: 'equipment-search' })">
          Search Equipment
        </fwb-button>
      </div>
    </div>
  </section>
</template>
