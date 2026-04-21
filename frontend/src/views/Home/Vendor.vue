<script setup>
/**
 * Home page for the vendor view
 * @module HomeVendor 
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbSpinner, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import RentalService from '../../services/rentalService'
import UserService from '../../services/userService'

/**
 * Auth store containing vendor identity and session data.
 */
const auth = useAuthStore()

/**
 * Router instance for navigation.
 */
const router = useRouter()

/**
 * Raw vendor rental records that is changed locally after fetch.
 * @type {import('vue').Ref<Array<any>>}
 */
const rentals = ref([])

/**
 * Loading state for rental data.
 */
const rentalsLoading = ref(true)

/**
 * Error state for rental loading.
 */
const rentalsError = ref(null)

/**
 * Rentals where users have expressed interest but not finalized booking.
 */
const interestedRenters = computed(() =>
  rentals.value
    .filter(r => !r.deleted && r.status === 'requesting')
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

/**
 * Returns true if current time is before rental start date.
 *
 * @param {any} rental - The rental object that contains rental information.
 * @returns {boolean} Returns true if current time is before rental start date. Otherwise, it returns false.
 */
function isBeforeRentalStart(rental) {
  const now = Date.now()
  return now < new Date(rental.start_date).getTime()
}

/**
 * Returns true if current time is within rental window.
 *
 * @param {any} rental - The rental object that contains rental information.
 * @returns {boolean} Returns true if current time is within rental window. Otherwise, it returns false.
 */
function isDuringRentalWindow(rental) {
  const now = Date.now()
  const start = new Date(rental.start_date).getTime()
  const end = new Date(rental.end_date).getTime()
  return now >= start && now <= end
}

/**
 * Rentals where equipment needs to be dropped off soon.
 */
const upcomingEquipmentDropOffs = computed(() =>
  rentals.value
    .filter(
      r => !r.deleted && r.status === 'active' && isBeforeRentalStart(r)
    )
    .sort((a, b) => new Date(a.end_date) - new Date(b.end_date))
)

/**
 * Rentals where equipment is currently active and will be picked up soon.
 */
const upcomingEquipmentPickUps = computed(() =>
  rentals.value
    .filter(r => !r.deleted && r.status === 'active' && isDuringRentalWindow(r))
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

/**
 * Formats ISO date into a readable string.
 *
 * @param {string} iso - The date formatted in ISO format.
 * @returns {string} Human readable date string.
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
 * Loads all rentals belonging to the current vendor.
 */
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

/**
 * Initial data fetch on component mount.
 */
onMounted(() => {
  loadVendorRentals()
})
</script>

<template>
  <section class="max-w-6xl mx-auto space-y-10">
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
          <router-link
            v-for="rental in interestedRenters"
            :key="rental.id"
            :to="{ name: 'rental_view', params: { id: rental.id } }"
            class="block !max-w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
          >
            <fwb-card class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow">
              <div class="p-4 space-y-1">
                <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
                <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
                <p class="text-sm text-gray-600">{{ formatDate(rental.start_date) }} - {{ formatDate(rental.end_date) }}</p>
                <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
                <p class="text-sm font-semibold text-amber-700">Proposed price: ${{ rental.agreed_price }}</p>
              </div>
            </fwb-card>
          </router-link>
        </div>
        <p v-else class="text-sm text-amber-800">No requested rentals.</p>
      </div>

      <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <h3 class="text-lg font-semibold text-blue-900 mb-3">Upcoming Equipment Drop Off</h3>
        <div v-if="upcomingEquipmentDropOffs.length" class="space-y-3">
          <router-link
            v-for="rental in upcomingEquipmentDropOffs"
            :key="rental.id"
            :to="{ name: 'rental_view', params: { id: rental.id } }"
            class="block !max-w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
          >
            <fwb-card class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow">
              <div class="p-4 space-y-1">
                <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
                <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
                <p class="text-sm text-gray-600">{{ formatDate(rental.start_date) }}</p>
                <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
                <p class="text-sm font-semibold text-blue-700">Agreed Price: ${{ rental.agreed_price }}</p>
              </div>
            </fwb-card>
          </router-link>
        </div>
        <p v-else class="text-sm text-blue-800">No upcoming equipment drop-offs.</p>
      </div>

      <div class="rounded-xl border border-cyan-200 bg-cyan-50 p-4">
        <h3 class="text-lg font-semibold text-cyan-900 mb-3">Upcoming Equipment Pick Ups</h3>
        <div v-if="upcomingEquipmentPickUps.length" class="space-y-3">
          <router-link
            v-for="rental in upcomingEquipmentPickUps"
            :key="rental.id"
            :to="{ name: 'rental_view', params: { id: rental.id } }"
            class="block !max-w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2"
          >
            <fwb-card class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow">
              <div class="p-4 space-y-1">
                <p class="text-sm font-semibold text-gray-900">{{ rental.equipment_name }}</p>
                <p class="text-sm text-gray-700">Renter: {{ rental.renter_name }}</p>
                <p class="text-sm text-gray-600">{{ formatDate(rental.end_date) }}</p>
                <p class="text-sm text-gray-700">{{ rental.location || 'No location set' }}</p>
                <p class="text-sm font-semibold text-cyan-700">Agreed Price: ${{ rental.agreed_price }}</p>
              </div>
            </fwb-card>
          </router-link>
        </div>
        <p v-else class="text-sm text-cyan-800">No upcoming equipment pick ups.</p>
      </div>

    </div>
  </section>
</template>
