<script lang="js" setup>

import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbSpinner, FwbImg, FwbRating, FwbListGroup, FwbListGroupItem, FwbCard, FwbAvatar } from 'flowbite-vue'
import EquipmentService from '../../services/equipmentService'
import UserService from '../../services/userService'
import ReviewService from '../../services/reviewService'

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

const route = useRoute()
const router = useRouter()
const ownerData = ref()
const equipmentData = ref()
const equipmentReviews = ref()
const equipmentID = ref()
const dataLoaded = ref(false)
const numRatingsText = ref('')
const numRatings = ref(0)
const averageRating = ref(0.0)

function reviewDateFormatting(isoDate) {
    const date = new Date(isoDate)
    let day = date.getDate()
    let month = date.getMonth()
    let year = date.getFullYear()

    return months[month] + " " + day.toString() + ", " + year.toString()
}

async function sortEquipmentReviewsDescending() {
    equipmentReviews.value.sort((a, b) => new Date(b.date) - new Date(a.date))
}

async function addSubmitterName() {
    for (let i = 0; i < equipmentReviews.value.length; i++) {
        // Getting the submitter's user information
        let userInfo = await UserService.getUser(equipmentReviews.value[i].submitter_id)

        // Adding the submitter's name to the dictionary
        equipmentReviews.value[i].submitter_name = userInfo.name;
    }
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
        // Getting the equipment id from the route
        equipmentID.value = route.params.id

        // Getting the equipment data
        equipmentData.value = await EquipmentService.getEquipmentById(equipmentID.value)

        // Getting the equipment reviews data
        equipmentReviews.value = await ReviewService.getReviewsForModel("equipment", equipmentData.value.id)
        await sortEquipmentReviewsDescending()
        await addSubmitterName()
        await computeReviewData()

        // Getting the equipment owner's data
        ownerData.value = await UserService.getUser(equipmentData.value.owner_id)

        // Displaying the page to the user
        dataLoaded.value = true
    }
    catch (error) {
        console.error("Error loading equipment data:", error)

        // Alerting the user that the equipment data could not be loaded
        alert("Error: Equipment data could not be loaded.")
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
            <fwb-img
                alt="flowbite-vue"
                size="max-w-md"
                img-class="rounded-lg"
                src="../../../image.jpg" 
            />
            <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ equipmentData.name }}</h5>
            <fwb-rating :rating="averageRating" review-link="#ReviewsTitle" :review-text="numRatingsText">
                <template #besideText>
                    <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                        {{ averageRating }} out of 5
                    </p>
                </template>
            </fwb-rating>
            <fwb-list-group class="w-auto">
                <fwb-list-group-item><b class="mr-1">Price:</b> ${{ equipmentData.price }}</fwb-list-group-item>
                <fwb-list-group-item>
                    <b class="mr-1">Vendor:</b>
                    <router-link :to="{ name: 'view_profile', params: { id: ownerData.id } }" class="text-blue-600 hover:underline">
                        {{ ownerData.name }}
                    </router-link>
                </fwb-list-group-item>
                <fwb-list-group-item class="!flex !flex-col !items-start">
                    <b class="mr-1">Description:</b>
                    <span>{{ equipmentData.description }}</span>
                </fwb-list-group-item>
            </fwb-list-group>
            <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
            <h1 id="ReviewsTitle" class="text-2xl font-bold text-gray-800 mb-6">Reviews</h1>
            <div v-if="numRatings == 0" class="space-y-4">
                <p class="font-normal text-gray-700 dark:text-gray-400">This equipment has not been reviewed</p>
            </div>
            <div v-else class="space-y-4">
                <fwb-card v-for="review in equipmentReviews" :key="review.id" class="!max-w-full">
                    <div class="space-y-3 p-5">
                        <div class="flex items-center space-x-4">
                            <fwb-avatar size="md" img="" rounded />
                            <p class="font-normal text-gray-700 dark:text-gray-400">{{ review.submitter_name }}</p>
                        </div>
                        <fwb-rating size="sm" :rating="review.rating">
                            <template #besideText>
                                <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                                    {{ review.rating }} out of 5
                                </p>
                            </template>
                        </fwb-rating>
                        <p class="text-sm font-bold text-gray-900 dark:text-white">Reviewed on {{ reviewDateFormatting(review.date) }}</p>
                        <p class="font-normal text-gray-700 dark:text-gray-400">{{ review.review }}</p>
                    </div>
                </fwb-card>
            </div>
        </div>
    </div>
</template>

<style scoped>

</style>