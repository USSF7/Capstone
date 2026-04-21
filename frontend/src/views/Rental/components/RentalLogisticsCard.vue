<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbButton, FwbListGroup, FwbListGroupItem, FwbRating } from 'flowbite-vue'
import RentalService from '../../../services/rentalService'

/**
 * Component props
 * @property {Object} rentalData - Rental record being displayed
 * @property {Object} vendorData - Vendor user info
 * @property {Object} renterData - Renter user info
 * @property {number} currentUserId - Logged-in user ID
 */
const props = defineProps({
  rentalData: { type: Object, required: true },
  vendorData: { type: Object, required: true },
  renterData: { type: Object, required: true },
  currentUserId: { type: Number, required: true },
})

/**
 * Component events
 * - open-review-user: opens review modal for counterparty
 * - rental-updated: emits updated rental object after API changes
 */
const emit = defineEmits(['open-review-user', 'rental-updated'])

/**
 * Router instance for navigation.
 */
const router = useRouter()

/**
 * True if rental is in a problematic state
 */
const isDisputedOrDenied = computed(() =>
  props.rentalData.status === 'denied' || props.rentalData.status === 'disputed' || props.rentalData.status === 'cancelled'
)

/**
 * True if rental has been completed
 */
const isReturned = computed(() => props.rentalData.status === 'returned')

/**
 * True if viewer is the vendor
 */
const isVendorViewer = computed(() => props.currentUserId === props.rentalData?.vendor_id)

/**
 * True if viewer is the renter
 */
const isRenterViewer = computed(() => props.currentUserId === props.rentalData?.renter_id)

/**
 * True if vendor is currently deciding on a request
 */
const isPendingVendorDecision = computed(
  () => isVendorViewer.value && props.rentalData?.status === 'requesting'
)

/**
 * True if current user still needs to approve a request
 */
const isAwaitingMyApproval = computed(() => {
  if (props.rentalData?.status !== 'requesting') return false
  if (isVendorViewer.value) return !props.rentalData?.vendor_approved
  if (isRenterViewer.value) return !props.rentalData?.renter_approved
  return false
})

/**
 * True if user approved but other party has not yet approved
 */
const isAwaitingCounterpartyApproval = computed(() => {
  if (props.rentalData?.status !== 'requesting') return false
  if (isVendorViewer.value) return !!props.rentalData?.vendor_approved && !props.rentalData?.renter_approved
  if (isRenterViewer.value) return !!props.rentalData?.renter_approved && !props.rentalData?.vendor_approved
  return false
})

/**
 * Determines if vendor can mark rental as returned
 */
const canMarkReturned = computed(() => {
  if (!isVendorViewer.value) return false
  if (props.rentalData?.status !== 'active') return false
  if (!props.rentalData?.end_date) return false

  return new Date() > new Date(props.rentalData.end_date)
})

/**
 * Label for review button depending on user role
 */
const reviewUserLabel = computed(() => (isVendorViewer.value ? 'Review Renter' : 'Review Vendor'))

/**
 * Current timestamp, which is used for time-based eligibility checks
 */
const currentTime = ref(Date.now())

/**
 * Interval ID for periodic time updates
 */
let currentTimeIntervalId = null

/**
 * True if rental is active but has not started yet
 */
const isPreStartActiveRental = computed(() => {
  if (props.rentalData?.status !== 'active' || !props.rentalData?.start_date) return false
  return new Date() < new Date(props.rentalData.start_date)
})

/**
 * True if rental is eligible for renegotiation
 */
const isRenegotiationEligible = computed(() => {
  if (props.rentalData?.status !== 'active' || !props.rentalData?.start_date) return false

  const startDate = new Date(props.rentalData.start_date)
  return startDate.getTime() - currentTime.value > 7 * 24 * 60 * 60 * 1000
})

/**
 * True if current user has already submitted a review
 */
const userAlreadyReviewed = computed(() => {
  const renterReviewed = props.rentalData?.renter_reviewed === true
  const vendorReviewed = props.rentalData?.vendor_reviewed === true

  return ((isRenterViewer.value && renterReviewed) || (isVendorViewer.value && vendorReviewed))
})

/**
 * Total duration of the rental in days
 */
const rentalDurationDays = computed(() => {
  if (!props.rentalData?.start_date || !props.rentalData?.end_date) return 1

  const start = new Date(props.rentalData.start_date)
  const end = new Date(props.rentalData.end_date)
  const msPerDay = 1000 * 60 * 60 * 24
  const dayDiff = Math.ceil((end - start) / msPerDay)
  return Number.isFinite(dayDiff) && dayDiff > 0 ? dayDiff : 1
})

/** 
 * Total rental price
 */
const totalPrice = computed(() => Number(props.rentalData?.agreed_price) || 0)

/**
 * Price per day based on total and duration
 */
const perDayPrice = computed(() => totalPrice.value / rentalDurationDays.value)

/**
 * Label indicating pricing stage based on rental status
 */
const priceStageLabel = computed(() => {
  const status = props.rentalData?.status

  if (status === 'requesting') return 'Offered'
  if (status === 'active') return 'Agreed'
  return 'Finalized'
})

/**
 * Label for counterparty (vendor or renter)
 */
const counterpartyLabel = computed(() => (isVendorViewer.value ? 'Renter' : 'Vendor'))

/**
 * Counterparty user object
 */
const counterpartyData = computed(() => (isVendorViewer.value ? props.renterData : props.vendorData))

/**
 * Maps rental status to progress percentage
 */
const mapStatusToPercent = new Map([
  ['requesting', 10.0],
  ['active', 70.0],
  ['returned', 100.0],
  ['disputed', 90.0],
  ['denied', 100.0],
  ['cancelled', 100.0],
])

/**
 * Returns progress percentage for a given rental status
 * @param {string} status - The status text
 * @returns {number} The status text mapped numerical value
 */
function getStatusPercent(status) {
  return mapStatusToPercent.get(status) || 0
}

/**
 * Formats date into readable US locale string
 * @param {string|Date} value The date in a string or Date object
 * @returns {string} A formatted date string
 */
function formatDateTime(value) {
  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/**
 * Formats number as USD currency string
 * @param {number} value The numerical value of the currency
 * @returns {string} The formatted currency in USD
 */
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Updates rental status via API
 * @param {string} nextStatus The next status in the rental cycle
 */
async function updateRequestStatus(nextStatus) {
  try {
    const updated = await RentalService.updateRental(
      props.rentalData.id,
      nextStatus,
      props.rentalData.location,
      props.rentalData.agreed_price,
      props.rentalData.deleted
    )
    emit('rental-updated', updated)
  } catch (error) {
    console.error('Failed to update rental status:', error)
    alert('Could not update this request. Please try again.')
  }
}

/**
 * Approves pending rental changes
 */
async function approveChanges() {
  try {
    const updated = await RentalService.updateRental(
      props.rentalData.id,
      props.rentalData.status,
      props.rentalData.location,
      props.rentalData.agreed_price,
      props.rentalData.deleted,
      true
    )
    emit('rental-updated', updated)
  } catch (error) {
    console.error('Failed to approve rental changes:', error)
    alert('Could not approve these changes. Please try again.')
  }
}

/**
 * Navigates to rental edit page
 */
function goToEditDetails() {
  router.push({ name: 'rental-edit', params: { id: props.rentalData.id } })
}

/**
 * Confirms and denies rental request
 */
function confirmAndDenyRequest() {
  const confirmed = window.confirm(
    'Are you sure you want to deny this rental request? This will notify the renter and mark the request as denied.'
  )
  if (!confirmed) return
  updateRequestStatus('denied')
}

/**
 * Confirms and cancels pending request
 */
function confirmAndCancelRequest() {
  const confirmed = window.confirm(
    'Are you sure you want to cancel this rental request? This will notify the vendor and mark the request as canceled.'
  )
  if (!confirmed) return
  updateRequestStatus('cancelled')
}

/**
 * Confirms and cancels active rental
 */
function confirmAndCancelActiveRental() {
  const confirmed = window.confirm(
    'Are you sure you want to cancel this rental? This will notify the other party and mark the rental as canceled.'
  )
  if (!confirmed) return
  updateRequestStatus('cancelled')
}

/**
 * Marks rental as returned after confirmation
 */
function confirmAndMarkReturned() {
  const confirmed = window.confirm(
    'Mark this rental as returned and complete the agreement? This action updates the rental to completed.'
  )
  if (!confirmed) return
  updateRequestStatus('returned')
}

/**
 * Starts timer for live time updates
 */
onMounted(() => {
  currentTimeIntervalId = setInterval(() => {
    currentTime.value = Date.now()
  }, 60000)
})

/**
 * Cleans up interval on component unmount
 */
onUnmounted(() => {
  if (currentTimeIntervalId) {
    clearInterval(currentTimeIntervalId)
    currentTimeIntervalId = null
  }
})
</script>

<template>
  <fwb-card class="!max-w-full">
    <div class="p-5 space-y-2">
      <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Logistics</span>
      <fwb-list-group class="w-auto">
        <fwb-list-group-item class="!flex !flex-col !items-start">
          <b class="mr-1">Dates:</b>
          <span>{{ formatDateTime(rentalData.start_date) }} through {{ formatDateTime(rentalData.end_date) }}</span>
        </fwb-list-group-item>
        <fwb-list-group-item>
          <b class="mr-1">{{ priceStageLabel }} Price:</b>
          {{ formatCurrency(totalPrice) }}
        </fwb-list-group-item>
        <fwb-list-group-item>
          <b class="mr-1">{{ priceStageLabel }} Price Per Day:</b>
          {{ formatCurrency(perDayPrice) }}
          <span class="ml-1 text-xs text-gray-500">({{ rentalDurationDays }} day{{ rentalDurationDays === 1 ? '' : 's' }})</span>
        </fwb-list-group-item>
        <fwb-list-group-item class="!flex !flex-col !items-start">
          <b class="mr-1">Meeting Location:</b>
          <span>{{ rentalData.location }}</span>
        </fwb-list-group-item>
        <fwb-list-group-item>
          <b class="mr-1">{{ counterpartyLabel }}:</b>
          <router-link
            :to="{ name: 'view_profile', params: { id: counterpartyData.id } }"
            class="mr-1 text-blue-600 hover:underline"
          >
            {{ counterpartyData.name }}
          </router-link>
          <fwb-rating size="sm" :rating=counterpartyData.averageRating />
        </fwb-list-group-item>
      </fwb-list-group>

      <fwb-progress
        v-if="isDisputedOrDenied"
        class="font-normal text-gray-700 dark:text-gray-400"
        :progress="getStatusPercent(rentalData.status)"
        size="md"
        color="red"
        :label="rentalData.status_text || 'Rental status updated'"
      />
      <fwb-progress
        v-else-if="isReturned"
        class="font-normal text-gray-700 dark:text-gray-400"
        :progress="getStatusPercent(rentalData.status)"
        size="md"
        color="green"
        :label="rentalData.status_text || 'Rental status updated'"
      />
      <fwb-progress
        v-else
        class="font-normal text-gray-700 dark:text-gray-400"
        :progress="getStatusPercent(rentalData.status)"
        size="md"
        :label="rentalData.status_text || 'Rental status updated'"
      />

      <div v-if="isPreStartActiveRental || isRenegotiationEligible" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p class="text-sm text-blue-800 mb-2" v-if="isRenegotiationEligible">
          This rental starts more than a week from now, so either party can renegotiate the terms.
        </p>
        <p class="text-sm text-blue-800 mb-2" v-else>
          This rental is active but has not started yet, so either party can still cancel it.
        </p>
        <div class="flex flex-wrap gap-2">
          <fwb-button v-if="isPreStartActiveRental" color="red" @click="confirmAndCancelActiveRental">Cancel Rental</fwb-button>
          <fwb-button v-if="isRenegotiationEligible" color="light" @click="goToEditDetails">Renegotiate Terms</fwb-button>
        </div>
      </div>

      <div v-if="isReturned" class="flex mt-4">
        <fwb-button
          v-if="userAlreadyReviewed === false"
          color="default"
          class="flex-1"
          @click="$emit('open-review-user')"
        >
          {{ reviewUserLabel }}
        </fwb-button>
        <fwb-button
          v-else
          color="default"
          class="flex-1"
          @click="$emit('open-review-user')"
          disabled
        >
          {{ reviewUserLabel }}
        </fwb-button>
      </div>

      <div v-if="isAwaitingMyApproval" class="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <p class="text-sm font-medium text-amber-900 mb-2">Approval Needed</p>
        <div class="flex flex-wrap gap-2">
          <fwb-button color="green" @click="approveChanges">Approve Changes</fwb-button>
          <fwb-button v-if="isVendorViewer" color="red" @click="confirmAndDenyRequest">Deny Request</fwb-button>
          <fwb-button v-if="isRenterViewer" color="red" @click="confirmAndCancelRequest">Cancel Request</fwb-button>
          <fwb-button color="light" @click="goToEditDetails">Edit Details</fwb-button>
        </div>
      </div>

      <div v-if="isAwaitingCounterpartyApproval" class="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <p class="text-sm text-gray-700 mb-2">You approved these details. Waiting on the other party to approve.</p>
        <div class="flex flex-wrap gap-2">
          <fwb-button v-if="isVendorViewer" color="red" @click="confirmAndDenyRequest">Deny Request</fwb-button>
          <fwb-button v-if="isRenterViewer" color="red" @click="confirmAndCancelRequest">Cancel Request</fwb-button>
          <fwb-button color="light" @click="goToEditDetails">Edit Details</fwb-button>
        </div>
      </div>

      <div v-if="canMarkReturned" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-sm text-green-800 mb-2">The rental period has ended. You can mark this rental as returned.</p>
        <fwb-button color="green" @click="confirmAndMarkReturned">Mark as Returned</fwb-button>
      </div>
    </div>
  </fwb-card>
</template>
