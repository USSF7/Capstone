<!-- View a specific rental's details -->
<script lang="js" setup>

import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { FwbSpinner, FwbCard, FwbImg, FwbRating, FwbProgress, FwbButton } from 'flowbite-vue'
import RentalService from '../../services/rentalService'
import UserService from '../../services/userService'
import ReviewService from '../../services/reviewService'
import AuthService from '../../services/authService'
import ReviewEquipment from './ReviewEquipment.vue'
import ReviewUser from './ReviewUser.vue'

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

const route = useRoute()
const rentalID = ref()
const rentalData = ref()
const vendorData = ref()
const userData = ref()
const dataLoaded = ref(false)
const equipmentReviews = ref()
const numRatings = ref(0)
const numRatingsText = ref('')
const averageRating = ref(0.0)
const showReviewEquipmentModal = ref(false)
const showReviewUserModal = ref(false)

function dateFormatting(isoDate) {
    const date = new Date(isoDate)
    let day = date.getDate()
    let month = date.getMonth()
    let year = date.getFullYear()

    return months[month] + " " + day.toString() + ", " + year.toString()
}

async function computeReviewData() {
    // Computing the total number of ratings
    numRatings.value = equipmentReviews.value.length

    if (numRatings.value == 1) {
        numRatingsText.value = numRatings.value.toString() + " review"
    }
    else {
        numRatingsText.value = numRatings.value.toString() + " reviews"
    }

    // Computing the average rating
    if (numRatings.value == 0) {
        averageRating.value = 0.0
    }
    else {
        let sumRatings = 0.0
        for (let i = 0; i < equipmentReviews.value.length; i++) {
            sumRatings += equipmentReviews.value[i].rating
        }
        averageRating.value = sumRatings / numRatings.value
    }
}

async function loadData() {
    try {
        // Getting the rental id from the route
        rentalID.value = route.params.id

        // Getting the rental with equipment data
        rentalData.value = await RentalService.getRentalWithEquipment(rentalID.value)

        // Getting the vendor's data
        vendorData.value = await UserService.getUser(rentalData.value.vendor_id)

        // Getting the user's data
        userData.value = await AuthService.getMe()

        // Getting the equipment reviews data
        equipmentReviews.value = await ReviewService.getReviewsForModel("equipment", rentalData.value.equipment[0].id)
        await computeReviewData()

        // Displaying the page to the user
        dataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting rental data:", error)

        // Alerting the user that the rental data could not be loaded
        alert("Error: Rental data could not be loaded.")
    }
}

onMounted(async () => {
    await loadData()
})

</script>

<template>
    <div v-if="dataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div class="space-y-4">
            <review-equipment
                v-if="showReviewEquipmentModal"
                :equipmentName=rentalData.equipment[0].name
                :equipmentID=rentalData.equipment[0].id
                :submitterID=userData.id
                @close="showReviewEquipmentModal = false"
            />
            <review-user 
                v-if="showReviewUserModal"
                :userName=vendorData.name
                :userID=vendorData.id
                :submitterID=userData.id
                @close="showReviewUserModal = false"
            />
            <div class="grid grid-cols-2 gap-4">
                <fwb-card class="!max-w-full">
                    <div class="p-5 space-y-2">
                        <fwb-img
                            alt="flowbite-vue"
                            img-class="rounded-lg"
                            src="../../../image.jpg"
                        />
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ rentalData.equipment[0].name }}</h5>
                        <fwb-rating :rating="averageRating" review-link="#" :review-text="numRatingsText">
                            <template #besideText>
                                <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                                    {{ averageRating }} out of 5
                                </p>
                            </template>
                        </fwb-rating>
                        <p class="font-normal text-gray-700 dark:text-gray-400"><b>Price:</b> ${{ rentalData.agreed_price }}</p>
                        <p class="font-normal text-gray-700 dark:text-gray-400">
                            <b>Vendor: </b>
                            <router-link :to="{ name: 'view_profile', params: { id: vendorData.id } }" class="text-blue-600 hover:underline">
                                {{ vendorData.name }}
                            </router-link>
                        </p>
                        <p class="font-normal text-gray-700 dark:text-gray-400"><b>Description:</b> <br> {{ rentalData.equipment[0].description }}</p>
                    </div>
                </fwb-card>
                <fwb-card class="!max-w-full">
                    <div class="p-5">
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Messaging</h5>
                    </div>
                </fwb-card>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <fwb-card class="!max-w-full">
                    <div class="p-5 space-y-2">
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Logistics</h5>
                        <p class="font-normal text-gray-700 dark:text-gray-400"><b>Dates:</b> {{ dateFormatting(rentalData.start_date) }} through {{ dateFormatting(rentalData.end_date) }}</p>
                        <p class="font-normal text-gray-700 dark:text-gray-400"><b>Meeting Location:</b> {{ rentalData.location }}</p>
                        <fwb-progress v-if="(rentalData.status === 'denied') || (rentalData.status === 'disputed')" class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rentalData.status)" size="md" color="red" :label=mapStatusToText.get(rentalData.status) />
                        <fwb-progress v-else-if="rentalData.status === 'returned'" class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rentalData.status)" size="md" color="green" :label=mapStatusToText.get(rentalData.status) />
                        <fwb-progress v-else class="font-normal text-gray-700 dark:text-gray-400" :progress="mapStatusToPercent.get(rentalData.status)" size="md" :label=mapStatusToText.get(rentalData.status) />
                        <div class="flex space-x-3 mt-4">
                            <fwb-button v-if="rentalData.status === 'returned'" color="default" class="flex-1" @click="showReviewEquipmentModal = true">Review Equipment</fwb-button>
                            <fwb-button v-else color="default" class="flex-1" @click="showReviewEquipmentModal = true" disabled>Review Equipment</fwb-button>
                            <fwb-button v-if="rentalData.status === 'returned'" color="default" class="flex-1" @click="showReviewUserModal = true">Review Vendor</fwb-button>
                            <fwb-button v-else color="default" class="flex-1" @click="showReviewUserModal = true" disabled>Review Vendor</fwb-button>
                        </div>
                    </div>
                </fwb-card>
                <fwb-card class="!max-w-full">
                    <div class="p-5 space-y-2">
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Google Maps</h5>
                    </div>
                </fwb-card>
            </div>
        </div>
    </div>
</template>