<!-- View of all rentals a user is a part of -->
<!-- The view is currently getting rentals by the renter -->
<script lang="js" setup>

import { ref, onMounted } from 'vue'
import { FwbCard, FwbProgress } from 'flowbite-vue'
import RentalService from '../../services/rentalService'

// ********************************************************************** //
// These user IDs need to be updated when account login gets implemented. //
// Potentially use localStorage.                                          //
// ********************************************************************** //
const userId = 10

const mapStatusToPercent = new Map([
    ["disputed", 10.0],
    ["pending", 40.0],
    ["active", 70.0],
    ["returned", 100.0]
])

const mapStatusToText = new Map([
    ["disputed", "Rental is currently being disputed"],
    ["pending", "Vendor has accepted the rental"],
    ["active", "Rental is active"],
    ["returned", "Rental has been returned"]
])

const userRentalsData = ref()

async function filterOutCanceledRentals() {
    userRentalsData.value = userRentalsData.value.filter(rental => rental.status !== "canceled")
}

async function loadUserRentalsData() {
    try {
        // Loading in the user's rentals
        userRentalsData.value = await RentalService.getRentalsByRenter(userId)
        await filterOutCanceledRentals()
    }
    catch (error) {
        console.error("Error getting user rentals data:", error)

        // Alerting the user that the user's rentals data could not be loaded
        alert("Error: Account rentals data could not be loaded.")
    }
}

onMounted(async () => {
    await loadUserRentalsData()
})

</script>

<template>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">My Rentals</h1>
    <div class="space-y-4">
        <fwb-card v-for="rental in userRentalsData" :key="rental.id" class="!max-w-full">
            <div class="space-y-2 p-5">
                <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ rental.id }}</h5>
                <p class="font-normal text-gray-700 dark:text-gray-400">Price: ${{ rental.agreed_price }}</p>
                <p class="font-normal text-gray-700 dark:text-gray-400">Dates: {{ rental.start_date }} to {{ rental.end_date }}</p>
                <fwb-progress class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rental.status)" size="md" :label=mapStatusToText.get(rental.status) />
            </div>
        </fwb-card>
    </div>
</template>

<style scoped>

</style>