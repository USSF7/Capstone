<!-- View of all rentals a user is a part of -->
<script lang="js" setup>
/**
 * The rental index page, which displays a user's current and previous rentals.
 * @module RentalIndex
 */

import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { FwbTab, FwbTabs, FwbSpinner } from 'flowbite-vue'
import RentalService from '../../services/rentalService'
import AuthService from '../../services/authService'
import RentalSummaryCard from './components/RentalSummaryCard.vue'

/**
 * Maps backend rental statuses to progress bar percentages.
 */
const mapStatusToPercent = new Map([
    ["requesting", 10.0],
    ["active", 70.0],
    ["returned", 100.0],
    ["disputed", 90.0],
    ["denied", 100.0],
    ["cancelled", 100.0]
])

/**
 * Vue Router instance
 */
const router = useRouter()

/**
 * Logged-in user data
 */
const userData = ref()

/**
 * All rentals where the user is either renter or vendor
 */
const userRentalsData = ref([])

/**
 * Currently selected tab in the user interface
 */
const activeTab = ref('requested rentals')

/**
 * Controls whether the page content is shown
 */
const userDataLoaded = ref(false)

/**
 * Removes rentals that are marked as deleted.
 */
async function filterOutDeletedRentals() {
    userRentalsData.value = userRentalsData.value.filter(rental => rental.deleted == false)
}

/**
 * Sorts rentals in-place by start date (descending).
 */
async function sortRentalsByStartDateDescending() {
    userRentalsData.value.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
}

/**
 * Loads all rental data relevant to the current user.
 */
async function loadUserRentalsData() {
    try {
        // Loading in the user's data
        userData.value = await AuthService.getMe()

        // Load all rentals where this user is involved (renter or vendor).
        const renterRentals = await RentalService.getRentalsWithEquipmentByRenter(userData.value.id)
        let vendorRentals = []
        if (userData.value.vendor) {
            const vendorRentalsBasic = await RentalService.getRentalsByVendor(userData.value.id)
            vendorRentals = await Promise.all(
                vendorRentalsBasic.map((rental) => RentalService.getRentalWithEquipment(rental.id))
            )
        }

        const rentalsById = new Map()
        for (const rental of [...renterRentals, ...vendorRentals]) {
            rentalsById.set(rental.id, rental)
        }

        userRentalsData.value = Array.from(rentalsById.values())
        await filterOutDeletedRentals()
        await sortRentalsByStartDateDescending()

        // Displaying the page to the user
        userDataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting user rentals data:", error)

        // Alerting the user that the user's rentals data could not be loaded
        alert("Error: Account rentals data could not be loaded.")
    }
}

/**
 * Rentals that are still in the request/negotiation phase.
 */
const requestedRentals = computed(() => {
    return userRentalsData.value.filter((rental) => rental.status === 'requesting')
})

/**
 * Rentals that are active but have not started yet.
 */
const upcomingRentals = computed(() => {
    const now = new Date()
    return userRentalsData.value.filter((rental) => {
        if (rental.status !== 'active') return false
        return new Date(rental.start_date) > now
    })
})

/**
 * Rentals that are active but have NOT started yet.
 */
const onLoanRentals = computed(() => {
    const now = new Date()
    return userRentalsData.value.filter((rental) => {
        if (rental.status !== 'active') return false
        return new Date(rental.start_date) <= now
    })
})

/**
 * Rentals that have been successfully completed.
 */
const completedRentals = computed(() => {
    return userRentalsData.value.filter((rental) => rental.status === 'returned')
})

/**
 * Rentals that ended negatively or were cancelled.
 */
const disputedRentals = computed(() => {
    return userRentalsData.value.filter(
        (rental) => rental.status === 'disputed' || rental.status === 'denied' || rental.status === 'cancelled'
    )
})

/**
 * Load all rental data when component mounts.
 */
onMounted(async () => {
    await loadUserRentalsData()
})

</script>

<template>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <h1 class="text-3xl font-bold text-gray-800 mb-6">My Rentals</h1>
        <fwb-tabs v-model="activeTab" class="p-5">
            <fwb-tab name="requested rentals" :title="`Requests (${requestedRentals.length})`">
                <div class="space-y-4">
                    <rental-summary-card
                        v-for="rental in requestedRentals"
                        :key="rental.id"
                        :rental="rental"
                        price-label="Offered Price"
                        :progress="mapStatusToPercent.get(rental.status)"
                        :progress-label="rental.status_text"
                        @select="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    />
                </div>
            </fwb-tab>
            <fwb-tab name="upcoming rentals" :title="`Upcoming (${upcomingRentals.length})`">
                <div class="space-y-4">
                    <rental-summary-card
                        v-for="rental in upcomingRentals"
                        :key="rental.id"
                        :rental="rental"
                        price-label="Agreed Price"
                        :progress="mapStatusToPercent.get(rental.status)"
                        :progress-label="rental.status_text"
                        @select="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    />
                </div>
            </fwb-tab>
            <fwb-tab name="on-loan rentals" :title="`On Loan (${onLoanRentals.length})`">
                <div class="space-y-4">
                    <rental-summary-card
                        v-for="rental in onLoanRentals"
                        :key="rental.id"
                        :rental="rental"
                        price-label="Agreed Price"
                        :progress="mapStatusToPercent.get(rental.status)"
                        :progress-label="rental.status_text"
                        @select="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    />
                </div>
            </fwb-tab>
            <fwb-tab name="completed rentals" :title="`Completed (${completedRentals.length})`">
                <div class="space-y-4">
                    <rental-summary-card
                        v-for="rental in completedRentals"
                        :key="rental.id"
                        :rental="rental"
                        price-label="Finalized Price"
                        :progress="mapStatusToPercent.get(rental.status)"
                        progress-color="green"
                        :progress-label="rental.status_text"
                        @select="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    />
                </div>
            </fwb-tab>
            <fwb-tab name="disputed rentals" :title="`Disputed (${disputedRentals.length})`">
                <div class="space-y-4">
                    <rental-summary-card
                        v-for="rental in disputedRentals"
                        :key="rental.id"
                        :rental="rental"
                        price-label="Finalized Price"
                        :progress="mapStatusToPercent.get(rental.status)"
                        progress-color="red"
                        :progress-label="rental.status_text"
                        @select="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    />
                </div>
            </fwb-tab>
        </fwb-tabs>
    </div>
</template>

<style scoped>

</style>