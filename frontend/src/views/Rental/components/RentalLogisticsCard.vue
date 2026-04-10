<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { FwbCard, FwbProgress, FwbButton, FwbListGroup, FwbListGroupItem, FwbRating } from 'flowbite-vue'
import RentalService from '../../../services/rentalService'

const props = defineProps({
  rentalData: { type: Object, required: true },
  vendorData: { type: Object, required: true },
  renterData: { type: Object, required: true },
  currentUserId: { type: Number, required: true },
})

const emit = defineEmits(['open-review-equipment', 'open-review-user', 'rental-updated'])
const router = useRouter()

const isDisputedOrDenied = computed(() =>
  props.rentalData.status === 'denied' || props.rentalData.status === 'disputed' || props.rentalData.status === 'cancelled'
)
const isReturned = computed(() => props.rentalData.status === 'returned')
const isVendorViewer = computed(() => props.currentUserId === props.rentalData?.vendor_id)
const isRenterViewer = computed(() => props.currentUserId === props.rentalData?.renter_id)
const isPendingVendorDecision = computed(
  () => isVendorViewer.value && props.rentalData?.status === 'requesting'
)
const isAwaitingMyApproval = computed(() => {
  if (props.rentalData?.status !== 'requesting') return false
  if (isVendorViewer.value) return !props.rentalData?.vendor_approved
  if (isRenterViewer.value) return !props.rentalData?.renter_approved
  return false
})
const isAwaitingCounterpartyApproval = computed(() => {
  if (props.rentalData?.status !== 'requesting') return false
  if (isVendorViewer.value) return !!props.rentalData?.vendor_approved && !props.rentalData?.renter_approved
  if (isRenterViewer.value) return !!props.rentalData?.renter_approved && !props.rentalData?.vendor_approved
  return false
})
const canMarkReturned = computed(() => {
  if (!isVendorViewer.value) return false
  if (props.rentalData?.status !== 'active') return false
  if (!props.rentalData?.end_date) return false

  return new Date() > new Date(props.rentalData.end_date)
})
const reviewUserLabel = computed(() => (isVendorViewer.value ? 'Review Renter' : 'Review Vendor'))
const canReviewEquipment = computed(() => !isVendorViewer.value)

const userAlreadyReviewed = computed(() => {
  const renterReviewed = props.rentalData?.renter_reviewed === true
  const vendorReviewed = props.rentalData?.vendor_reviewed === true

  return ((isRenterViewer.value && renterReviewed) || (isVendorViewer.value && vendorReviewed))
})

const equipmentAlreadyReviewed = computed(() => {
  const equipmentReviewed = props.rentalData?.equipment_reviewed === true
  return equipmentReviewed
})

const rentalDurationDays = computed(() => {
  if (!props.rentalData?.start_date || !props.rentalData?.end_date) return 1

  const start = new Date(props.rentalData.start_date)
  const end = new Date(props.rentalData.end_date)
  const msPerDay = 1000 * 60 * 60 * 24
  const dayDiff = Math.ceil((end - start) / msPerDay)
  return Number.isFinite(dayDiff) && dayDiff > 0 ? dayDiff : 1
})
const totalPrice = computed(() => Number(props.rentalData?.agreed_price) || 0)
const perDayPrice = computed(() => totalPrice.value / rentalDurationDays.value)
const priceStageLabel = computed(() => {
  const status = props.rentalData?.status

  if (status === 'requesting') return 'Offered'
  if (status === 'active') return 'Agreed'
  return 'Finalized'
})

const counterpartyLabel = computed(() => (isVendorViewer.value ? 'Renter' : 'Vendor'))
const counterpartyData = computed(() => (isVendorViewer.value ? props.renterData : props.vendorData))

const mapStatusToPercent = new Map([
  ['requesting', 10.0],
  ['active', 70.0],
  ['returned', 100.0],
  ['disputed', 90.0],
  ['denied', 100.0],
  ['cancelled', 100.0],
])

function getStatusPercent(status) {
  return mapStatusToPercent.get(status) || 0
}

function formatDateTime(value) {
  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

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

function goToEditDetails() {
  router.push({ name: 'rental-edit', params: { id: props.rentalData.id } })
}

function confirmAndDenyRequest() {
  const confirmed = window.confirm(
    'Are you sure you want to deny this rental request? This will notify the renter and mark the request as denied.'
  )
  if (!confirmed) return
  updateRequestStatus('denied')
}

function confirmAndCancelRequest() {
  const confirmed = window.confirm(
    'Are you sure you want to cancel this rental request? This will notify the vendor and mark the request as canceled.'
  )
  if (!confirmed) return
  updateRequestStatus('cancelled')
}

function confirmAndMarkReturned() {
  const confirmed = window.confirm(
    'Mark this rental as returned and complete the agreement? This action updates the rental to completed.'
  )
  if (!confirmed) return
  updateRequestStatus('returned')
}
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

      <div v-if="isReturned" class="flex space-x-3 mt-4">
        <fwb-button
          v-if="(canReviewEquipment === true) && (equipmentAlreadyReviewed === false)"
          color="default"
          class="flex-1"
          @click="$emit('open-review-equipment')"
        >
          Review Equipment
        </fwb-button>
        <fwb-button
          v-else-if="canReviewEquipment"
          color="default"
          class="flex-1"
          @click="$emit('open-review-equipment')"
          disabled
        >
          Review Equipment
        </fwb-button>
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
