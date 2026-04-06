<!-- View a specific rental's details -->
<script lang="js" setup>

import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbSpinner, FwbCard } from 'flowbite-vue'
import RentalService from '../../services/rentalService'
import UserService from '../../services/userService'
import ReviewService from '../../services/reviewService'
import AuthService from '../../services/authService'
import ReviewEquipment from './ReviewEquipment.vue'
import ReviewUser from './ReviewUser.vue'
import RentalEquipmentCard from './components/RentalEquipmentCard.vue'
import RentalMessagingCard from './components/RentalMessagingCard.vue'
import RentalLogisticsCard from './components/RentalLogisticsCard.vue'
import GoogleMap from '../../components/GoogleMap.vue'

const route = useRoute()
const router = useRouter()
const rentalID = ref()
const rentalData = ref()
const vendorData = ref()
const renterData = ref()
const userData = ref()
const otherParticipantID = ref(null)
const dataLoaded = ref(false)
const showReviewEquipmentModal = ref(false)
const showReviewUserModal = ref(false)
let pollIntervalId = null

const POLL_INTERVAL_MS = 10000

const primaryEquipment = computed(() => rentalData.value?.equipment?.[0] || null)

const isVendorViewer = computed(() =>
    !!(userData.value && rentalData.value && userData.value.id === rentalData.value.vendor_id)
)

const reviewUserTarget = computed(() => {
    if (!rentalData.value || !vendorData.value || !renterData.value) return null
    return isVendorViewer.value ? renterData.value : vendorData.value
})

const meetingPoint = computed(() => {
    if (rentalData.value?.meeting_lat == null || rentalData.value?.meeting_lng == null) return null
    return {
        lat: rentalData.value.meeting_lat,
        lng: rentalData.value.meeting_lng,
    }
})

const mapMarkers = computed(() => {
    const markers = []

    if (renterData.value?.latitude != null && renterData.value?.longitude != null) {
        markers.push({
            lat: renterData.value.latitude,
            lng: renterData.value.longitude,
            title: `Renter: ${renterData.value.name}`,
            label: `<strong>Renter</strong><br>${renterData.value.name}`,
            color: '#2563EB',
        })
    }

    if (vendorData.value?.latitude != null && vendorData.value?.longitude != null) {
        markers.push({
            lat: vendorData.value.latitude,
            lng: vendorData.value.longitude,
            title: `Vendor: ${vendorData.value.name}`,
            label: `<strong>Vendor</strong><br>${vendorData.value.name}`,
            color: '#059669',
        })
    }

    if (meetingPoint.value) {
        markers.push({
            lat: meetingPoint.value.lat,
            lng: meetingPoint.value.lng,
            title: 'Meeting Location',
            label: `<strong>Meeting Location</strong><br>${rentalData.value?.location || ''}`,
            color: '#DC2626',
            selected: true,
        })
    }

    return markers
})

const mapCenter = computed(() => {
    if (meetingPoint.value) return meetingPoint.value
    if (renterData.value?.latitude != null && renterData.value?.longitude != null) {
        return { lat: renterData.value.latitude, lng: renterData.value.longitude }
    }
    if (vendorData.value?.latitude != null && vendorData.value?.longitude != null) {
        return { lat: vendorData.value.latitude, lng: vendorData.value.longitude }
    }
    return null
})

async function computeEquipmentReviewData() {
    for (let i = 0; i < rentalData.value.equipment.length; i++) {
        if (!rentalData.value.equipment[i].equipmentReviews) {
            rentalData.value.equipment[i].equipmentReviews = []
        }

        // Computing the total number of ratings
        let numRatings = rentalData.value.equipment[i].equipmentReviews.length

        if (numRatings == 1) {
            rentalData.value.equipment[i].numRatingsText = numRatings.toString() + " review"
        }
        else {
            rentalData.value.equipment[i].numRatingsText = numRatings.toString() + " reviews"
        }

        // Computing the average rating
        if (numRatings == 0) {
            rentalData.value.equipment[i].averageRating = 0.0
        }
        else {
            let sumRatings = 0.0
            for (let j = 0; j < rentalData.value.equipment[i].equipmentReviews.length; j++) {
                sumRatings += rentalData.value.equipment[i].equipmentReviews[j].rating
            }

            let avgRating = sumRatings / numRatings
            rentalData.value.equipment[i].averageRating = avgRating.toFixed(2)
        }
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

async function loadData() {
    try {
        // Getting the rental id from the route
        rentalID.value = route.params.id

        // Getting the user's data
        userData.value = await AuthService.getMe()

        // Getting the rental with equipment data
        rentalData.value = await RentalService.getRentalWithEquipment(rentalID.value)

        // Ensure only renter/vendor can view this page
        const isParticipant = [rentalData.value.renter_id, rentalData.value.vendor_id].includes(userData.value.id)
        if (!isParticipant) {
            alert("You are not authorized to view this rental.")
            router.push({ name: 'rentals' })
            return
        }

        otherParticipantID.value = userData.value.id === rentalData.value.vendor_id
            ? rentalData.value.renter_id
            : rentalData.value.vendor_id

        // Getting the vendor's data
        vendorData.value = await UserService.getUser(rentalData.value.vendor_id)
        renterData.value = await UserService.getUser(rentalData.value.renter_id)

        // Getting the equipment reviews data for the all of the equipment items
        for (let i = 0; i < rentalData.value.equipment.length; i++) {
            if (primaryEquipment.value) {
                rentalData.value.equipment[i].equipmentReviews = await ReviewService.getReviewsForModel("equipment", rentalData.value.equipment[i].id)
            } else {
                rentalData.value.equipment[i].equipmentReviews = []
            }
        }
        await computeEquipmentReviewData()

        // Getting the reviews for the renter and the vendor
        vendorData.value.userReviews = await ReviewService.getReviewsForModel("user", vendorData.value.id)
        renterData.value.userReviews = await ReviewService.getReviewsForModel("user", renterData.value.id)
        await computeUserReviewData(vendorData)
        await computeUserReviewData(renterData)

        // Displaying the page to the user
        dataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting rental data:", error)

        if ((error?.message || '').toLowerCase().includes('forbidden') || (error?.message || '').includes('403')) {
            alert("You are not authorized to view this rental.")
            router.push({ name: 'rentals' })
            return
        }

        // Alerting the user that the rental data could not be loaded
        alert("Error: Rental data could not be loaded.")
    }
}

async function pollForUpdates() {
    if (!rentalID.value || !dataLoaded.value) return

    try {
        const latestRental = await RentalService.getRentalWithEquipment(rentalID.value)

        // If participant changed or rental is no longer accessible, route out.
        if (!userData.value || ![latestRental.renter_id, latestRental.vendor_id].includes(userData.value.id)) {
            router.push({ name: 'rentals' })
            return
        }

        const oldEquipmentId = primaryEquipment.value?.id
        const newEquipmentId = latestRental?.equipment?.[0]?.id

        // Reset the rental data only if the primary equipment changed.
        if (oldEquipmentId !== newEquipmentId) {
            rentalData.value = latestRental
        }

        // Re-fetch review aggregate only if the primary equipment changed.
        if (oldEquipmentId !== newEquipmentId) {
            for (let i = 0; i < rentalData.value.equipment.length; i++) {
                if (primaryEquipment.value) {
                    rentalData.value.equipment[i].equipmentReviews = await ReviewService.getReviewsForModel('equipment', rentalData.value.equipment[i].id)
                } else {
                    rentalData.value.equipment[i].equipmentReviews = []
                }
                await computeEquipmentReviewData()
            }
        }
    }
    catch (error) {
        // Silent during polling to avoid disrupting users with transient failures.
        console.warn('Rental polling failed:', error?.message || error)
    }
}

async function handleRentalUpdated() {
  // Re-fetch full rental with equipment
  await loadData()
}

onMounted(async () => {
    await loadData()

    pollIntervalId = setInterval(() => {
        pollForUpdates()
    }, POLL_INTERVAL_MS)
})

onUnmounted(() => {
    if (pollIntervalId) {
        clearInterval(pollIntervalId)
        pollIntervalId = null
    }
})

</script>

<template>
    <div v-if="dataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div class="space-y-4">
            <review-equipment
                v-if="showReviewEquipmentModal && primaryEquipment"
                :equipmentName="primaryEquipment.name"
                :equipmentID="primaryEquipment.id"
                :submitterID="userData.id"
                :rentalID="rentalData.id"
                @close="showReviewEquipmentModal = false"
            />
            <review-user 
                v-if="showReviewUserModal && reviewUserTarget"
                :userName="reviewUserTarget.name"
                :userID="reviewUserTarget.id"
                :submitterID="userData.id"
                :rentalID="rentalData.id"
                @close="showReviewUserModal = false"
            />

            <div class="grid grid-cols-2 gap-4" v-if="vendorData && renterData">
                <rental-equipment-card
                    :rental-data="rentalData"
                    :current-user-id="userData.id"
                />

                <rental-messaging-card
                    :current-user-id="userData.id"
                    :other-user-id="otherParticipantID"
                    :rental-id="rentalData.id"
                />
            </div>

            <div class="grid grid-cols-2 gap-4" v-if="vendorData && renterData">
                <rental-logistics-card
                    :rentalData="rentalData"
                    :currentUserId="userData.id"
                    :vendorData="vendorData"
                    :renterData="renterData"
                    @open-review-equipment="showReviewEquipmentModal = true"
                    @open-review-user="showReviewUserModal = true"
                    @rental-updated="handleRentalUpdated"
                />

                <fwb-card class="!max-w-full">
                    <div class="p-5 space-y-2">
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Meeting Location</h5>
                        <GoogleMap
                            v-if="mapCenter && mapMarkers.length"
                            :center="mapCenter"
                            :markers="mapMarkers"
                            height="360px"
                        />
                        <p v-else class="text-sm text-gray-500">
                            Map is unavailable until renter/vendor locations are set.
                        </p>
                    </div>
                </fwb-card>
            </div>
        </div>
    </div>
</template>