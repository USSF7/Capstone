<!-- View of all rentals a user is a part of -->
<script lang="js" setup>

import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbImg, FwbTab, FwbTabs, FwbSpinner } from 'flowbite-vue'
import RentalService from '../../services/rentalService'
import AuthService from '../../services/authService'

const months = [
    "January", 
    "February", 
    "March", 
    "April", 
    "May", 
    "June", 
    "July", 
    "August", 
    "September", 
    "October", 
    "November", 
    "December"
]

const mapStatusToPercent = new Map([
    ["requesting", 10.0],
    ["accepted", 40.0],
    ["active", 70.0],
    ["returned", 100.0],
    ["disputed", 90.0],
    ["denied", 100.0]
])

const mapStatusToText = new Map([
    ["requesting", "You have requested the rental"],
    ["accepted", "Vendor has accepted the rental"],
    ["active", "Rental is active"],
    ["returned", "Rental has been completed"],
    ["disputed", "Rental is being disputed"],
    ["denied", "Vendor has denied the rental"]
])

const router = useRouter()
const userData = ref()
const userRentalsData = ref()
const activeTab = ref('active rentals')
const userDataLoaded = ref(false)

function dateFormatting(isoDate) {
    const date = new Date(isoDate)
    let day = date.getDate()
    let month = date.getMonth()
    let year = date.getFullYear()

    return months[month] + " " + day.toString() + ", " + year.toString()
}

async function filterOutDeletedRentals() {
    userRentalsData.value = userRentalsData.value.filter(rental => rental.deleted == false)
}

async function sortRentalsByStartDateDescending() {
    userRentalsData.value.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
}

async function loadUserRentalsData() {
    try {
        // Loading in the user's data
        userData.value = await AuthService.getMe()

        // Loading in the user's rentals
        userRentalsData.value = await RentalService.getRentalsWithEquipmentByRenter(userData.value.id)
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

const filterActiveRentals = computed(() => {
    return userRentalsData.value.filter(rental => (rental.status !== 'disputed') && (rental.status !== 'denied') && (rental.status !== 'returned'))
})

const filterCompletedRentals = computed(() => {
    return userRentalsData.value.filter(rental => rental.status === 'returned')
})

const filterRejectedDisputedRentals = computed(() => {
    return userRentalsData.value.filter(rental => (rental.status === 'disputed') || (rental.status === 'denied'))
})

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
            <fwb-tab name="active rentals" title="Active Rentals">
                <div class="space-y-4">
                    <fwb-card
                        v-for="rental in filterActiveRentals"
                        :key="rental.id"
                        class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
                        @click="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    >
                        <div class="flex flex-col p-5 gap-4">
                            <div class="flex gap-4">
                                <fwb-img
                                    alt="flowbite-vue"
                                    img-class="w-48 rounded-lg"
                                    src="../../../image.jpg"
                                />
                                <div class="flex flex-col space-y-2">
                                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ rental.equipment[0].name }}</h5>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Price:</b> ${{ rental.agreed_price }}</p>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Dates:</b> {{ dateFormatting(rental.start_date) }} through {{ dateFormatting(rental.end_date) }}</p>
                                </div>
                            </div>
                            <fwb-progress class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rental.status)" size="md" :label=mapStatusToText.get(rental.status) />
                        </div>
                    </fwb-card>
                </div>
            </fwb-tab>
            <fwb-tab name="completed rentals" title="Completed Rentals">
                <div class="space-y-4">
                    <fwb-card
                        v-for="rental in filterCompletedRentals"
                        :key="rental.id"
                        class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
                        @click="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    >
                        <div class="flex flex-col p-5 gap-4">
                            <div class="flex gap-4">
                                <fwb-img
                                    alt="flowbite-vue"
                                    img-class="w-48 rounded-lg"
                                    src="../../../image.jpg"
                                />
                                <div class="flex flex-col space-y-2">
                                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ rental.equipment[0].name }}</h5>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Price:</b> ${{ rental.agreed_price }}</p>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Dates:</b> {{ dateFormatting(rental.start_date) }} through {{ dateFormatting(rental.end_date) }}</p>
                                </div>
                            </div>
                            <fwb-progress class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rental.status)" size="md" color="green" :label=mapStatusToText.get(rental.status) />
                        </div>
                    </fwb-card>
                </div>
            </fwb-tab>
            <fwb-tab name="rejected and disputed rentals" title="Rejected / Disputed Rentals">
                <div class="space-y-4">
                    <fwb-card
                        v-for="rental in filterRejectedDisputedRentals"
                        :key="rental.id"
                        class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow"
                        @click="router.push({ name: 'rental_view', params:{ id: rental.id } })"
                    >
                        <div class="flex flex-col p-5 gap-4">
                            <div class="flex gap-4">
                                <fwb-img
                                    alt="flowbite-vue"
                                    img-class="w-48 rounded-lg"
                                    src="../../../image.jpg"
                                />
                                <div class="flex flex-col space-y-2">
                                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ rental.equipment[0].name }}</h5>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Price:</b> ${{ rental.agreed_price }}</p>
                                    <p class="font-normal text-gray-700 dark:text-gray-400"><b>Dates:</b> {{ dateFormatting(rental.start_date) }} through {{ dateFormatting(rental.end_date) }}</p>
                                </div>
                            </div>
                            <fwb-progress class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rental.status)" size="md" color="red" :label=mapStatusToText.get(rental.status) />
                        </div>
                    </fwb-card>
                </div>
            </fwb-tab>
        </fwb-tabs>
    </div>
</template>

<style scoped>

</style>