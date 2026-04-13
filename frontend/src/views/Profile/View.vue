<!-- View a specific users profile details -->
<script lang="js" setup>

import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { FwbAvatar, FwbRating, FwbListGroup, FwbListGroupItem, FwbButton, FwbCard, FwbSpinner } from 'flowbite-vue'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/solid'
import UserService from '../../services/userService'
import EquipmentService from '../../services/equipmentService'
import reviewService from '../../services/reviewService'
import authService from '../../services/authService'
import aiService from '../../services/aiService'
import router from '../../router'
import ReviewUserEdit from '../Rental/ReviewUserEdit.vue'

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

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

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
const submitterNameCache = new Map()
const showReviewUserModal = ref(false)
const popUpReviewId = ref(0)
const popUpReviewRating = ref(0.0)
const popUpReviewText = ref('')
const vendorEquipment = ref([])
const hasVendorEquipment = computed(() => Array.isArray(vendorEquipment.value) && vendorEquipment.value.length > 0)
const viewedUserIsVendor = computed(() => Boolean(userData.value?.vendor || hasVendorEquipment.value))
const isViewingAnotherUser = computed(() => Number(userData.value?.id) !== Number(viewingUserData.value?.id))

function reviewDateFormatting(isoDate) {
    const date = new Date(isoDate)
    let day = date.getDate()
    let month = date.getMonth()
    let year = date.getFullYear()

    return months[month] + " " + day.toString() + ", " + year.toString()
}

function dateFormatting(isoDate) {
    const date = new Date(isoDate)
    return date.toLocaleDateString()
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

function createEquipmentRequest() {
    router.push({ name: 'rental_create', query: { vendorId: userData.value.id } })
}

async function deleteReview(reviewId) {
    // Double checking if the user wants to delete their review
    const confirmed = confirm("Are you sure you want to delete your review?\n\nWarning: Deleting this review will permanently remove it. You will only be able to submit another review about this user after completing another rental with them.")
    
    if (confirmed === true) {
        // Deleting the user's review
        await reviewService.switchDeletedReviewStatus(reviewId, true)

        // Reloading user data
        window.location.reload()
    }
}

async function editReview(reviewId) {
    // Get the review data
    let review = await reviewService.getReview(reviewId)

    // Store review information
    popUpReviewId.value = reviewId
    popUpReviewRating.value = review.rating
    popUpReviewText.value = review.review

    // Open pop-up menu
    showReviewUserModal.value = true
}

async function sortUserReviewsDescending() {
    userReviews.value.sort((a, b) => new Date(b.date) - new Date(a.date))
}

async function addSubmitterName() {
    if (!userReviews.value?.length) {
        return
    }

    try {
        const submitterIds = [...new Set(userReviews.value.map(r => r.submitter_id).filter(Boolean))]

        await Promise.all(submitterIds.map(async (submitterId) => {
            if (!submitterNameCache.has(submitterId)) {
                const userInfo = await UserService.getUser(submitterId)
                submitterNameCache.set(submitterId, {
                    name: userInfo?.name || 'Unknown user',
                    picture: userInfo?.picture || ''
                })
            }
        }))

        for (let i = 0; i < userReviews.value.length; i++) {
            const submitterId = userReviews.value[i].submitter_id
            const cached = submitterNameCache.get(submitterId)

            userReviews.value[i].submitter_name = cached?.name || 'Unknown user'
            userReviews.value[i].picture = cached?.picture || ''
        }
    }
    catch (error) {
        console.warn('Unable to enrich review submitter names:', error)
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
        let avgRating = sumRatings / numRatings.value
        averageRating.value = avgRating.toFixed(2)
    }
}

async function loadReviewSummary() {
    reviewSummary.value = ''

    // Only summarize when there is at least one review.
    if (numRatings.value === 0) {
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
        userDataLoaded.value = false
        reviewSummary.value = ''
        reviewSummaryLoading.value = false

        // Fetch viewer + target profile in parallel.
        userID.value = route.params.id
        const [viewerData, targetUserData] = await Promise.all([
            authService.getMe(),
            UserService.getUser(userID.value),
        ])

        viewingUserData.value = viewerData
        userData.value = targetUserData
        const targetUserId = Number(userID.value)
        const [reviews, vendorEquipmentData] = await Promise.all([
            reviewService.getReviewsForModel("user", userData.value.id),
            EquipmentService.getEquipmentByOwner(targetUserId),
        ])

        userReviews.value = reviews
        vendorEquipment.value = Array.isArray(vendorEquipmentData) ? vendorEquipmentData : []
        await sortUserReviewsDescending()
        await computeReviewData()

        // Displaying the page to the user
        userDataLoaded.value = true

        // Fill non-critical data after initial render to reduce perceived load time.
        addSubmitterName()
        loadReviewSummary()
    }
    catch (error) {
        console.error("Error getting user data:", error)

        // Alerting the user that the user's data could not be loaded
        alert("Error: Account data could not be loaded.")
    }
}

watch(() => route.params.id, async (newId) => {
    if (!newId) {
        return
    }

    await loadUserData()
}, {
    immediate: true
})

</script>

<template>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div class="space-y-4">
            <review-user-edit
                v-if="showReviewUserModal"
                :userName="userData.name"
                :userPicture="userData.picture"
                :userID="userData.id"
                :submitterID="viewingUserData.id"
                :reviewId="popUpReviewId"
                :reviewRating="popUpReviewRating"
                :reviewText="popUpReviewText"
                @close="showReviewUserModal = false"
            />
            
            <fwb-avatar bordered size="xl" :img="userData.picture ? `${BACKEND_URL}/${userData.picture}` : ''" />

            <h1 class="text-3xl font-bold text-gray-800">{{ userData.name }}</h1>
            <p class="text-sm text-gray-600">{{ userData.email }}</p>
            <fwb-rating :rating="averageRating" review-link="#ReviewsTitle" :review-text="numRatingsText">
                <template #besideText>
                    <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                        {{ averageRating }} out of 5
                    </p>
                </template>
            </fwb-rating>
            <div v-if="isViewingAnotherUser && viewedUserIsVendor" class="space-y-4">
                <div class="rounded-lg border border-gray-200 bg-white p-4 space-y-4">
                    <div>
                        <h2 class="text-lg font-semibold text-gray-900">Available Equipment</h2>
                        <p class="text-sm text-gray-600">{{ vendorEquipment.length }} item{{ vendorEquipment.length === 1 ? '' : 's' }} listed</p>
                    </div>

                    <ul v-if="hasVendorEquipment" class="space-y-3">
                        <li
                            v-for="item in vendorEquipment.slice(0, 6)"
                            :key="item.id"
                            class="rounded-md border border-gray-100"
                        >
                            <router-link
                                :to="{ name: 'equipment-view', params: { id: item.id } }"
                                class="p-3 block rounded-md hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                            >
                                <p class="font-medium text-gray-900 underline-offset-2">{{ item.name }}</p>
                                <p class="text-sm text-gray-600">${{ item.price }}/day • {{ item.condition || 'Condition not set' }}</p>
                                <fwb-rating size="sm" :rating="item.average_rating || 0" />
                            </router-link>
                        </li>
                    </ul>

                    <p v-else class="text-sm text-gray-500">This vendor has no equipment listed yet.</p>

                    <p v-if="vendorEquipment.length > 6" class="text-xs text-gray-500">
                        +{{ vendorEquipment.length - 6 }} more item{{ vendorEquipment.length - 6 === 1 ? '' : 's' }}
                    </p>

                    <fwb-button
                        v-if="hasVendorEquipment"
                        class="w-auto"
                        color="default"
                        pill
                        @click="createEquipmentRequest"
                    >
                        Request Equipment
                    </fwb-button>
                </div>
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
                <fwb-card class="!max-w-full border border-gray-200 bg-gray-100/70">
                    <div class="space-y-2 p-5">
                        <p class="text-sm font-semibold tracking-wide text-gray-700 dark:text-gray-400">AI Summary</p>
                        <p v-if="reviewSummaryLoading" class="font-normal text-gray-700 dark:text-gray-400">Generating summary...</p>
                        <p v-else-if="reviewSummary" class="font-normal text-gray-700 dark:text-gray-400">{{ reviewSummary }}</p>
                        <p v-else class="font-normal text-gray-700 dark:text-gray-400">Summary unavailable right now.</p>
                    </div>
                </fwb-card>
                <fwb-card v-for="review in userReviews" :key="review.id" class="!max-w-full">
                    <div class="space-y-3 p-5">
                        <div v-if="review.submitter_id == viewingUserData.id" class="flex items-center justify-between">
                            <div class="flex items-center space-x-4">
                                <fwb-avatar size="md" :img="review.picture ? `${BACKEND_URL}/${review.picture}` : ''" rounded />
                                <span class="font-normal text-gray-700 dark:text-gray-400">
                                    {{ review.submitter_name }}
                                </span>
                            </div>
                            <div class="flex space-x-2">
                                <fwb-button @click="editReview(review.id)" color="blue" size="md" square>
                                    <PencilIcon class="w-4 h-4" />
                                </fwb-button>
                                <fwb-button @click="deleteReview(review.id)" color="red" size="md" square>
                                    <TrashIcon class="w-5 h-5" />
                                </fwb-button>
                            </div>
                        </div>
                        <div v-else class="flex items-center space-x-4">
                            <fwb-avatar size="md" :img="review.picture ? `${BACKEND_URL}/${review.picture}` : ''" rounded />
                            <router-link
                                :to="{ name: 'view_profile', params: { id: review.submitter_id } }"
                                class="font-normal text-blue-700 dark:text-gray-400 hover:underline"
                            >
                                {{ review.submitter_name }}
                            </router-link>
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