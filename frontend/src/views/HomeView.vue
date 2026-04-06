<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbSpinner, FwbButton, FwbBadge } from 'flowbite-vue'
import { useAuthStore } from '../stores/auth'
import RentalService from '../services/rentalService'
import LocationService from '../services/locationService'
import UserService from '../services/userService'

const auth = useAuthStore()
const router = useRouter()

const rentals = ref([])
const nearbyEquipment = ref([])
const rentalsLoading = ref(true)
const equipmentLoading = ref(true)
const rentalsError = ref(null)
const equipmentError = ref(null)

const isRenter = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.renter)
const isVendor = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.vendor)

const activeRentals = computed(() =>
  rentals.value
    .filter(r => !r.deleted && ['requesting', 'accepted', 'active'].includes(r.status))
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

const interestedRenters = computed(() =>
  rentals.value
    .filter(r => !r.deleted && r.status === 'requesting')
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

function isBeforeRentalStart(rental) {
  const now = Date.now()
  return now < new Date(rental.start_date).getTime()
}

function isDuringRentalWindow(rental) {
  const now = Date.now()
  const start = new Date(rental.start_date).getTime()
  const end = new Date(rental.end_date).getTime()
  return now >= start && now <= end
}

const upcomingEquipmentDropOffs = computed(() =>
  rentals.value
    .filter(
      r => !r.deleted && (r.status === 'accepted' || (r.status === 'active' && isBeforeRentalStart(r)))
    )
    .sort((a, b) => new Date(a.end_date) - new Date(b.end_date))
)

const upcomingEquipmentPickUps = computed(() =>
  rentals.value
    .filter(r => !r.deleted && r.status === 'active' && isDuringRentalWindow(r))
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
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
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

async function loadVendorRentals() {
  rentalsLoading.value = true
  rentalsError.value = null
  try {
    const vendorRentals = await RentalService.getRentalsByVendor(auth.user.id)

    const renterIds = [...new Set(vendorRentals.map(r => r.renter_id))]
    const renterEntries = await Promise.all(
      renterIds.map(async (id) => {
        const user = await UserService.getUser(id)
        return [id, user.name]
      })
    )
    const renterNameById = Object.fromEntries(renterEntries)

    rentals.value = await Promise.all(
      vendorRentals.map(async (rental) => {
        const rentalWithEquipment = await RentalService.getRentalWithEquipment(rental.id)
        return {
          ...rental,
          equipment_name: rentalWithEquipment.equipment?.length
            ? rentalWithEquipment.equipment.map(e => e.name).join(', ')
            : 'Equipment request',
          renter_name: renterNameById[rental.renter_id] || 'Unknown renter',
        }
      })
    )
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
  if (isVendor.value) {
    loadVendorRentals()
  } else if (isRenter.value) {
    loadRentals()
    loadNearbyEquipment()
  }
})
</script>

<template>
  <!-- Vendor Dashboard -->
  <section v-if="isVendor" class="max-w-6xl mx-auto space-y-10">
    <div class="bg-gradient-to-r from-emerald-700 to-teal-500 rounded-2xl p-8 text-white">
      <h1 class="text-3xl font-bold">Welcome back, {{ auth.user?.name?.split(' ')[0] }}</h1>
      <p class="mt-2 text-emerald-100">Track your incoming and completed rental activity.</p>
    </div>

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-gray-800">Vendor Rental Overview</h2>
      <fwb-button size="sm" color="light" @click="router.push({ name: 'rentals' })">
        View All Rentals
      </fwb-button>
    </div>

    <div v-if="rentalsLoading" class="flex justify-center py-8">
      <fwb-spinner size="10" />
    </div>

    <p v-else-if="rentalsError" class="text-red-600 text-sm">{{ rentalsError }}</p>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="rounded-xl border border-amber-200 bg-amber-50 p-4">
        <h3 class="text-lg font-semibold text-amber-900 mb-3">Interested Renters</h3>
        <div v-if="interestedRenters.length" class="space-y-3">
          <fwb-card
            v-for="rental in interestedRenters"
            :key="rental.id"
            class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
            @click="router.push({ name: 'rental_view', params: { id: rental.id } })"
          >
            <div class="p-4 space-y-1">
              <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
              <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
              <p class="text-sm text-gray-600">{{ formatDate(rental.start_date) }} - {{ formatDate(rental.end_date) }}</p>
              <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
              <p class="text-sm font-semibold text-amber-700">Proposed price: ${{ rental.agreed_price }}</p>
            </div>
          </fwb-card>
        </div>
        <p v-else class="text-sm text-amber-800">No requested rentals.</p>
      </div>

      <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <h3 class="text-lg font-semibold text-blue-900 mb-3">Upcoming Equipment Drop Off</h3>
        <div v-if="upcomingEquipmentDropOffs.length" class="space-y-3">
          <fwb-card
            v-for="rental in upcomingEquipmentDropOffs"
            :key="rental.id"
            class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
            @click="router.push({ name: 'rental_view', params: { id: rental.id } })"
          >
            <div class="p-4 space-y-1">
              <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
              <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
              <p class="text-sm text-gray-600">{{ formatDate(rental.start_date) }}</p>
              <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
              <p class="text-sm font-semibold text-blue-700">Agreed Price: ${{ rental.agreed_price }}</p>
            </div>
          </fwb-card>
        </div>
        <p v-else class="text-sm text-blue-800">No upcoming equipment drop-offs.</p>
      </div>

      <div class="rounded-xl border border-cyan-200 bg-cyan-50 p-4">
        <h3 class="text-lg font-semibold text-cyan-900 mb-3">Upcoming Equipment Pick Ups</h3>
        <div v-if="upcomingEquipmentPickUps.length" class="space-y-3">
          <fwb-card
            v-for="rental in upcomingEquipmentPickUps"
            :key="rental.id"
            class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
            @click="router.push({ name: 'rental_view', params: { id: rental.id } })"
          >
            <div class="p-4 space-y-1">
              <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
              <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
              <p class="text-sm text-gray-600">{{ formatDate(rental.end_date) }}</p>
              <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
              <p class="text-sm font-semibold text-cyan-700">Agreed Price: ${{ rental.agreed_price }}</p>
            </div>
          </fwb-card>
        </div>
        <p v-else class="text-sm text-cyan-800">No upcoming equipment pick ups.</p>
      </div>

    </div>
  </section>

  <!-- Renter Dashboard -->
  <section v-else-if="isRenter" class="max-w-5xl mx-auto space-y-10">
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
            <fwb-badge v-if="item.condition === 'Mint'" class="inline-block mt-1 mb-1" size="sm" type="default"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="item.condition === 'Above Average'" class="inline-block mt-1 mb-1" size="sm" type="green"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="item.condition === 'Average'" class="inline-block mt-1 mb-1" size="sm" type="yellow"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else class="inline-block mt-1 mb-1" size="sm" type="red"> {{ item.condition }} Condition </fwb-badge>
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
