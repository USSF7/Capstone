<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbSpinner, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../stores/auth'
import RentalService from '../services/rentalService'
import LocationService from '../services/locationService'

const auth = useAuthStore()
const router = useRouter()

const rentals = ref([])
const nearbyEquipment = ref([])
const rentalsLoading = ref(true)
const equipmentLoading = ref(true)
const rentalsError = ref(null)
const equipmentError = ref(null)

const isRenter = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.renter)

const activeRentals = computed(() =>
  rentals.value
    .filter(r => !r.deleted && ['requesting', 'accepted', 'active'].includes(r.status))
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

const statusPercent = { requesting: 10, accepted: 40, active: 70 }
const statusLabel = {
  requesting: 'Awaiting vendor response',
  accepted: 'Accepted — ready for pickup',
  active: 'Currently renting',
}
const statusColor = { requesting: 'yellow', accepted: 'blue', active: 'green' }

const hasLocation = computed(() => auth.user?.latitude != null && auth.user?.longitude != null)

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

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

onMounted(() => {
  if (isRenter.value) {
    loadRentals()
    loadNearbyEquipment()
  }
})
</script>

<template>
  <!-- Renter Dashboard -->
  <section v-if="isRenter" class="max-w-5xl mx-auto space-y-10">
    <!-- Welcome -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-2xl p-8 text-white">
      <h1 class="text-3xl font-bold">Welcome back, {{ auth.user?.name?.split(' ')[0] }}</h1>
      <p class="mt-2 text-blue-100">Here's what's happening with your rentals.</p>
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
        <fwb-card
          v-for="rental in activeRentals"
          :key="rental.id"
          class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
          @click="router.push({ name: 'rental_view', params: { id: rental.id } })"
        >
          <div class="flex flex-col p-5 gap-4">
            <div class="flex gap-5 items-start">
              <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold text-gray-900 truncate">
                  {{ rental.equipment?.[0]?.name || 'Equipment' }}
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
              :label="statusLabel[rental.status]"
            />
          </div>
        </fwb-card>
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

      <div v-else-if="nearbyEquipment.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <fwb-card
          v-for="item in nearbyEquipment"
          :key="item.id"
          class="cursor-pointer hover:shadow-lg transition-shadow"
          @click="router.push({ name: 'equipment-view', params: { id: item.id } })"
        >
          <div class="p-4">
            <div v-if="item.picture" class="mb-3">
              <img :src="item.picture" :alt="item.name" class="w-full h-32 object-cover rounded-lg" />
            </div>
            <div v-else class="mb-3 w-full h-32 bg-gray-100 rounded-lg flex items-center justify-center">
              <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h3 class="font-semibold text-gray-900 truncate">{{ item.name }}</h3>
            <p v-if="item.description" class="text-sm text-gray-500 mt-1 line-clamp-2">{{ item.description }}</p>
            <div class="flex items-center justify-between mt-3">
              <span class="text-lg font-bold text-blue-600">${{ item.price }}/day</span>
              <span class="text-sm text-gray-400">{{ item.distance_miles }} mi</span>
            </div>
            <p class="text-xs text-gray-400 mt-1">{{ item.owner_city }}, {{ item.owner_state }}</p>
          </div>
        </fwb-card>
      </div>

      <div v-else class="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
        <p class="text-gray-500">No equipment found nearby. Try expanding your search.</p>
        <fwb-button size="sm" class="mt-3" @click="router.push({ name: 'equipment-search' })">
          Search Equipment
        </fwb-button>
      </div>
    </div>
  </section>

  <!-- Default Landing (not signed in as renter) -->
  <section v-else class="max-w-3xl mx-auto text-center">
    <div class="py-16">
      <h1 class="text-4xl font-bold text-gray-800 mb-4">Welcome to SERA</h1>
      <p class="text-lg text-gray-500 mb-8">Share, rent, and discover equipment in your neighborhood.</p>
      <div v-if="!auth.isAuthenticated" class="flex justify-center gap-4">
        <fwb-button @click="router.push({ name: 'login' })">Get Started</fwb-button>
      </div>
    </div>
  </section>
</template>
