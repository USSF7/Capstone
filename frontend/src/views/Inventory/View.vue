<script lang="js" setup>

import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbSpinner, FwbImg, FwbRating, FwbListGroup, FwbListGroupItem, FwbCard, FwbAvatar, FwbBadge, FwbButton } from 'flowbite-vue'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/solid'
import authService from '../../services/authService'
import EquipmentService from '../../services/equipmentService'
import UserService from '../../services/userService'
import ReviewService from '../../services/reviewService'
import aiService from '../../services/aiService'
import ReviewEquipmentEdit from '../Rental/ReviewEquipmentEdit.vue'

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
const router = useRouter()
const viewingUserData = ref()
const ownerData = ref()
const equipmentData = ref()
const equipmentReviews = ref()
const equipmentID = ref()
const dataLoaded = ref(false)
const numRatingsText = ref('')
const numRatings = ref(0)
const averageRating = ref(0.0)
const reviewSummary = ref('')
const reviewSummaryLoading = ref(false)
const submitterNameCache = new Map()
const showReviewEquipmentModal = ref(false)
const popUpReviewId = ref(0)
const popUpReviewRating = ref(0.0)
const popUpReviewText = ref('')

async function deleteReview(reviewId) {
    // Deleting the user's review
    await ReviewService.switchDeletedReviewStatus(reviewId, true)

    // Reloading user data
    window.location.reload()
}

async function editReview(reviewId) {
    // Get the review data
    let review = await ReviewService.getReview(reviewId)

    // Store review information
    popUpReviewId.value = reviewId
    popUpReviewRating.value = review.rating
    popUpReviewText.value = review.review

    // Open pop-up menu
    showReviewEquipmentModal.value = true
}

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
    if (!equipmentReviews.value?.length) {
        return
    }

    try {
        const submitterIds = [...new Set(equipmentReviews.value.map(r => r.submitter_id).filter(Boolean))]

        await Promise.all(submitterIds.map(async (submitterId) => {
            if (!submitterNameCache.has(submitterId)) {
                const userInfo = await UserService.getUser(submitterId)
                submitterNameCache.set(submitterId, {
                    name: userInfo?.name || 'Unknown user',
                    picture: userInfo?.picture || ''
                })
            }
        }))

        for (let i = 0; i < equipmentReviews.value.length; i++) {
            const submitterId = equipmentReviews.value[i].submitter_id
            const cached = submitterNameCache.get(submitterId)

            equipmentReviews.value[i].submitter_name = cached?.name || 'Unknown user'
            equipmentReviews.value[i].picture = cached?.picture || ''
        }
    }
    catch (error) {
        console.warn('Unable to enrich equipment review submitter names:', error)
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
        let avgRating = sumRatings / numRatings.value
        averageRating.value = avgRating.toFixed(2)
    }
}

async function computeUserReviewData(userData) {
    if (!userData.value.userReviews) {
        userData.value.userReviews = []
    }

    // Computing the total number of ratings
    let numRatings = userData.value.userReviews.length

    if (numRatings == 1) {
        userData.value.numRatingsText = numRatings.toString() + " review"
    }
    else {
        userData.value.numRatingsText = numRatings.toString() + " reviews"
    }

    // Computing the average rating
    if (numRatings == 0) {
        userData.value.averageRating = 0.0
    }
    else {
        let sumRatings = 0.0
        for (let i = 0; i < userData.value.userReviews.length; i++) {
            sumRatings += userData.value.userReviews[i].rating
        }

        let avgRating = sumRatings / numRatings
        userData.value.averageRating = avgRating.toFixed(2)
    }
}

async function loadReviewSummary() {
    reviewSummary.value = ''

    if (!equipmentData.value?.id || numRatings.value === 0) {
        return
    }

    reviewSummaryLoading.value = true

    try {
        const response = await aiService.summarizeReviews('equipment', equipmentData.value.id)
        reviewSummary.value = (response?.summary || '').trim()
    }
    catch (error) {
        console.warn('Unable to load AI summary for equipment reviews:', error)
        reviewSummary.value = ''
    }
    finally {
        reviewSummaryLoading.value = false
    }
}

async function loadData() {
    try {
        dataLoaded.value = false
        reviewSummary.value = ''
        reviewSummaryLoading.value = false

        // Getting the viewing user data
        viewingUserData.value = await authService.getMe()

        // Getting the equipment id from the route
        equipmentID.value = route.params.id

        // Getting the equipment data
        equipmentData.value = await EquipmentService.getEquipmentById(equipmentID.value)

        // Fetch owner and reviews in parallel once equipment is available.
        const [reviewsData, ownerInfo] = await Promise.all([
            ReviewService.getReviewsForModel("equipment", equipmentData.value.id),
            UserService.getUser(equipmentData.value.owner_id),
        ])

        equipmentReviews.value = reviewsData
        await sortEquipmentReviewsDescending()
        await computeReviewData()
        ownerData.value = ownerInfo

        ownerData.value.userReviews = await ReviewService.getReviewsForModel("user", ownerData.value.id)
        await computeUserReviewData(ownerData)

        // Displaying the page to the user
        dataLoaded.value = true

        // Fill non-critical data after initial render to improve perceived speed.
        addSubmitterName()
        loadReviewSummary()
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
            <review-equipment-edit
                v-if="showReviewEquipmentModal"
                :equipmentName="equipmentData.name"
                :equipmentID="equipmentData.id"
                :equipmentPicture="equipmentData.picture"
                :submitterID="viewingUserData.id"
                :reviewId="popUpReviewId"
                :reviewRating="popUpReviewRating"
                :reviewText="popUpReviewText"
                @close="showReviewEquipmentModal = false"
            />
            <fwb-img
                v-if="equipmentData.picture"
                alt="flowbite-vue"
                size="max-w-md"
                img-class="rounded-lg mb-2"
                :src="`${BACKEND_URL}/${equipmentData.picture}`" 
            />
            <div v-else class="h-56 w-[420px] mb-2 bg-gray-100 rounded-lg border border-gray-300 flex items-center justify-center">
                <span class="text-sm text-gray-400">No image available</span>
            </div>
            <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ equipmentData.name }}</span>
            <fwb-rating :rating="averageRating" review-link="#ReviewsTitle" :review-text="numRatingsText">
                <template #besideText>
                    <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                        {{ averageRating }} out of 5
                    </p>
                </template>
            </fwb-rating>
            <fwb-badge v-if="equipmentData.condition === 'Mint'" class="inline-block" size="sm" type="default"> {{ equipmentData.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="equipmentData.condition === 'Above Average'" class="inline-block" size="sm" type="green"> {{ equipmentData.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="equipmentData.condition === 'Average'" class="inline-block" size="sm" type="yellow"> {{ equipmentData.condition }} Condition </fwb-badge>
            <fwb-badge v-else class="inline-block" size="sm" type="red"> {{ equipmentData.condition }} Condition </fwb-badge>
            <fwb-list-group class="w-auto">
                <fwb-list-group-item><b class="mr-1">Price:</b> ${{ equipmentData.price }}</fwb-list-group-item>
                <fwb-list-group-item>
                    <b class="mr-1">Vendor:</b>
                    <router-link :to="{ name: 'view_profile', params: { id: ownerData.id } }" class="text-blue-600 hover:underline">
                        {{ ownerData.name }}
                    </router-link>
                    <fwb-rating class="ml-1" size="sm" :rating=ownerData.averageRating />
                </fwb-list-group-item>
                <fwb-list-group-item class="!flex !flex-col !items-start">
                    <b class="mr-1">Description:</b>
                    <span>{{ equipmentData.description }}</span>
                </fwb-list-group-item>
            </fwb-list-group>
            <router-link
                v-if="viewingUserData?.id !== ownerData?.id"
                :to="{ name: 'rental_create', query: { vendorId: ownerData.id, equipmentId: equipmentData.id } }"
                class="inline-block text-white bg-blue-700 hover:bg-blue-800 font-medium rounded-lg text-sm px-5 py-2.5"
            >
                Request This Equipment
            </router-link>
            <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
            <h1 id="ReviewsTitle" class="text-2xl font-bold text-gray-800 mb-6">Reviews</h1>
            <div v-if="numRatings == 0" class="space-y-4">
                <p class="font-normal text-gray-700 dark:text-gray-400">This equipment has not been reviewed</p>
            </div>
            <div v-else class="space-y-4">
                <fwb-card class="!max-w-full border border-gray-200 bg-gray-100/70">
                    <div class="space-y-2 p-5">
                        <p class="text-sm font-semibold uppercase tracking-wide text-gray-700 dark:text-gray-400">AI Summary</p>
                        <p v-if="reviewSummaryLoading" class="font-normal text-gray-700 dark:text-gray-400">Generating summary...</p>
                        <p v-else-if="reviewSummary" class="font-normal text-gray-700 dark:text-gray-400">{{ reviewSummary }}</p>
                        <p v-else class="font-normal text-gray-700 dark:text-gray-400">Summary unavailable right now.</p>
                    </div>
                </fwb-card>
                <fwb-card v-for="review in equipmentReviews" :key="review.id" class="!max-w-full">
                    <div class="space-y-3 p-5">
                        <div v-if="review.submitter_id == viewingUserData.id" class="flex items-center justify-between">
                            <div class="flex items-center space-x-4">
                                <fwb-avatar size="md" :img="review.picture ? `${BACKEND_URL}/${review.picture}` : ''" rounded />
                                <p class="font-normal text-gray-700 dark:text-gray-400">{{ review.submitter_name }}</p>
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