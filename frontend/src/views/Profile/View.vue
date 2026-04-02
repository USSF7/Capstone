<!-- View a specific users profile details -->
<script lang="js" setup>

import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { FwbAvatar, FwbRating, FwbListGroup, FwbListGroupItem, FwbButton, FwbCard, FwbSpinner } from 'flowbite-vue'
import UserService from '../../services/userService'
import reviewService from '../../services/reviewService'
import authService from '../../services/authService'
import aiService from '../../services/aiService'
import router from '../../router'

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
const userID = ref()
const userData = ref()
const viewingUserData = ref()
const userDataLoaded = ref(false)
const userReviews = ref()
const reviewSummary = ref('')
const reviewSummaryLoading = ref(false)
const numRatings = ref(0)
const numRatingsText = ref('')
const averageRating = ref(0.0)

function dateFormatting(isoDate) {
    const date = new Date(isoDate)
    return date.toLocaleDateString()
}

function reviewDateFormatting(isoDate) {
    const date = new Date(isoDate)
    let day = date.getDate()
    let month = date.getMonth()
    let year = date.getFullYear()

    return months[month] + " " + day.toString() + ", " + year.toString()
}

function computeAge(dateOfBirth) {
    // Using date objects
    const currentDate = new Date()
    const birthDate = new Date(dateOfBirth)

    // Computing years of age
    let age = currentDate.getFullYear() - birthDate.getFullYear()

    // Subtracting a year if the user's birthday has not occurred
    const hadBirthday = (currentDate.getMonth() > birthDate.getMonth()) || ((currentDate.getMonth() == birthDate.getMonth()) && (currentDate.getDate() >= birthDate.getDate()))

    if (!hadBirthday) {
        age--
    }

    return age
}

function displayUserSiteStatus() {
    if ((userData.value.vendor == true) && (userData.value.renter == true)) {
        return "Vendor / Renter"
    }
    else if (userData.value.vendor == true) {
        return "Vendor"
    }
    else {
        return "Renter"
    }
}

function editAccount() {
    router.push({ name: 'edit_profile' })
}

async function sortUserReviewsDescending() {
    userReviews.value.sort((a, b) => new Date(b.date) - new Date(a.date))
}

async function addSubmitterName() {
    for (let i = 0; i < userReviews.value.length; i++) {
        // Getting the submitter's user information
        let userInfo = await UserService.getUser(userReviews.value[i].submitter_id)

        // Adding the submitter's name to the dictionary
        userReviews.value[i].submitter_name = userInfo.name;
    }
}

async function computeReviewData() {
    // Computing the total number of ratings
    numRatings.value = userReviews.value.length

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
        for (let i = 0; i < userReviews.value.length; i++) {
            sumRatings += userReviews.value[i].rating
        }
        averageRating.value = sumRatings / numRatings.value
    }
}

async function loadReviewSummary() {
    reviewSummary.value = ''

    // Only summarize vendor reviews and only when there is at least one review.
    if (!userData.value?.vendor || numRatings.value === 0) {
        return
    }

    reviewSummaryLoading.value = true

    try {
        const response = await aiService.summarizeReviews('user', userData.value.id)
        reviewSummary.value = (response?.summary || '').trim()
    }
    catch (error) {
        console.warn('Unable to load AI summary for vendor reviews:', error)
        reviewSummary.value = ''
    }
    finally {
        reviewSummaryLoading.value = false
    }
}

async function loadUserData() {
    try {
        // Getting the viewing user's data 
        viewingUserData.value = await authService.getMe()

        // Getting the user's data
        userID.value = route.params.id
        userData.value = await UserService.getUser(userID.value)
        userReviews.value = await reviewService.getReviewsForModel("user", userData.value.id)
        await sortUserReviewsDescending()
        await addSubmitterName()
        await computeReviewData()
        await loadReviewSummary()

        // Displaying the page to the user
        userDataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting user data:", error)

        // Alerting the user that the user's data could not be loaded
        alert("Error: Account data could not be loaded.")
    }
}

onMounted(async () => {
    await loadUserData()
})

</script>

<template>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div class="space-y-4">

            <!-- ************************************************* -->
            <!-- Avatar code needs to be updated in a later sprint -->
            <!-- ************************************************* -->
            <fwb-avatar bordered size="xl" img="" />

            <h1 class="text-3xl font-bold text-gray-800 mb-6">{{ userData.name }}</h1>
            <fwb-rating :rating="averageRating" review-link="#ReviewsTitle" :review-text="numRatingsText">
                <template #besideText>
                    <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                        {{ averageRating }} out of 5
                    </p>
                </template>
            </fwb-rating>
            <div v-if="userData.id != viewingUserData.id">
                <fwb-list-group class="w-auto">
                    <fwb-list-group-item><b>Email</b>: {{ userData.email }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Phone Number</b>: {{ userData.phone }}</fwb-list-group-item>
                    <fwb-list-group-item><b>State</b>: {{ userData.state }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Age</b>: {{ computeAge(userData.date_of_birth) }} years</fwb-list-group-item>
                    <fwb-list-group-item><b>User Type</b>: {{ (userData.vendor == true) ? 'Vendor' : 'Renter' }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Date Joined</b>: {{ dateFormatting(userData.created_at) }}</fwb-list-group-item>
                </fwb-list-group>
            </div>
            <div v-else class="space-y-4">
                <fwb-list-group class="w-auto">
                    <fwb-list-group-item><b>Email</b>: {{ userData.email }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Phone Number</b>: {{ userData.phone }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Street Address</b>: {{ userData.street_address }}</fwb-list-group-item>
                    <fwb-list-group-item><b>City</b>: {{ userData.city }}</fwb-list-group-item>
                    <fwb-list-group-item><b>State</b>: {{ userData.state }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Zip Code</b>: {{ userData.zip_code }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Age</b>: {{ computeAge(userData.date_of_birth) }} years</fwb-list-group-item>
                    <fwb-list-group-item><b>User Type</b>: {{ displayUserSiteStatus() }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Date Joined</b>: {{ dateFormatting(userData.created_at) }}</fwb-list-group-item>
                </fwb-list-group>
                <fwb-button class="w-24" color="default" pill @click="editAccount">Edit</fwb-button>
            </div>
            <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
            <h1 id="ReviewsTitle" class="text-2xl font-bold text-gray-800 mb-6">Reviews</h1>
            <div v-if="numRatings == 0" class="space-y-4">
                <p class="font-normal text-gray-700 dark:text-gray-400">This user has not been reviewed</p>
            </div>
            <div v-else class="space-y-4">
                <fwb-card v-if="userData.vendor == true" class="!max-w-full border border-blue-100 bg-blue-50/60">
                    <div class="space-y-2 p-5">
                        <p class="text-sm font-semibold uppercase tracking-wide text-gray-700 dark:text-gray-400">AI Summary</p>
                        <p v-if="reviewSummaryLoading" class="font-normal text-gray-700 dark:text-gray-400">Generating summary...</p>
                        <p v-else-if="reviewSummary" class="font-normal text-gray-700 dark:text-gray-400">{{ reviewSummary }}</p>
                        <p v-else class="font-normal text-gray-700 dark:text-gray-400">Summary unavailable right now.</p>
                    </div>
                </fwb-card>
                <fwb-card v-for="review in userReviews" :key="review.id" class="!max-w-full">
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