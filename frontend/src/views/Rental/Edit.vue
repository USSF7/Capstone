<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbButton, FwbInput, FwbSpinner } from 'flowbite-vue'
import AuthService from '../../services/authService'
import RentalService from '../../services/rentalService'
import locationService from '../../services/locationService'
import RentalMeetingLocationField from './components/RentalMeetingLocationField.vue'

/**
 * Vue Route instance
 */
const route = useRoute()

/**
 * Vue Router instance
 */
const router = useRouter()

/**
 * Reactive rental ID extracted from the route parameters.
 */
const rentalId = computed(() => Number(route.params.id))

/**
 * User interface state flag controlling loading state.
 */
const loading = ref(true)

/**
 * User interface state flag controlling submission state.
 */
const submitting = ref(false)

/**
 * Error message displayed in the UI when validation or API calls fail.
 */
const error = ref('')

/**
 * Authenticated user object fetched from backend.
 */
const currentUser = ref(null)

/**
 * Rental object being edited.
 */
const rental = ref(null)

/**
 * Form input agreed price
 */
const agreedPrice = ref('')

/**
 * Form input start date
 */
const startDate = ref('')

/**
 * Form input end date
 */
const endDate = ref('')

/**
 * Form input location
 */
const location = ref('')

/**
 * Meeting location latitude coordinate
 */
const meetingLat = ref(null)

/**
 * Meeting location longitude coordinate
 */
const meetingLng = ref(null)

/**
 * Minimum allowed start date
 */
const minimumStartDate = ref('')

/**
 * Pads a number with a leading zero if needed (used for date formatting).
 *
 * @param {number|string} value - Numeric value to pad.
 * @returns {string} Two-digit string representation.
 */
function pad(value) {
	return String(value).padStart(2, '0')
}

/**
 * Adds a number of hours to a Date object.
 *
 * @param {Date} date - Base date.
 * @param {number} hours - Number of hours to add.
 * @returns {Date} New Date instance with added hours.
 */
function addHours(date, hours) {
	const result = new Date(date)
	result.setHours(result.getHours() + hours)
	return result
}

/**
 * Converts a Date or ISO string into a datetime-local input-compatible string.
 *
 * @param {string|Date} value - Date value to convert.
 * @returns {string} Formatted datetime-local string or empty string if invalid.
 */
function toDateTimeLocalValue(value) {
	if (!value) return ''
	const date = new Date(value)
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

/**
 * Converts a datetime-local string into a UTC ISO string for backend storage.
 *
 * @param {string} value - Local datetime string (YYYY-MM-DDTHH:mm)
 * @returns {string} ISO 8601 UTC string.
 */
function toUtcIsoString(value) {
	if (!value) return ''
	return new Date(value).toISOString()
}

/**
 * Loads rental data and validates user authorization.
 */
async function loadData() {
	try {
		error.value = ''
		currentUser.value = await AuthService.getMe()
		rental.value = await RentalService.getRental(rentalId.value)

		const isParticipant = [rental.value.renter_id, rental.value.vendor_id].includes(currentUser.value.id)
		if (!isParticipant) {
			error.value = 'You are not authorized to edit this rental.'
			return
		}

		agreedPrice.value = String(rental.value.agreed_price)
		startDate.value = toDateTimeLocalValue(rental.value.start_date)
		endDate.value = toDateTimeLocalValue(rental.value.end_date)
		minimumStartDate.value = toDateTimeLocalValue(addHours(new Date(), 2))
		location.value = rental.value.location || ''
		meetingLat.value = rental.value.meeting_lat ?? null
		meetingLng.value = rental.value.meeting_lng ?? null
	} catch (e) {
		error.value = e.message || 'Failed to load rental details.'
	} finally {
		loading.value = false
	}
}

/**
 * Saves updated rental information to the backend.
 */
async function saveChanges() {
	if (!agreedPrice.value || Number(agreedPrice.value) <= 0) {
		error.value = 'Offer price must be greater than 0.'
		return
	}

	if (!startDate.value || !endDate.value) {
		error.value = 'Start and end dates are required.'
		return
	}

	if (minimumStartDate.value && new Date(startDate.value) < new Date(minimumStartDate.value)) {
		error.value = 'Start date must be at least 2 hours in the future.'
		return
	}

	if (new Date(endDate.value) <= new Date(startDate.value)) {
		error.value = 'End date must be after start date.'
		return
	}

	if (!location.value.trim()) {
		error.value = 'Meeting location is required.'
		return
	}

	try {
		submitting.value = true
		error.value = ''

		let finalMeetingLat = meetingLat.value
		let finalMeetingLng = meetingLng.value
		if ((finalMeetingLat == null || finalMeetingLng == null) && location.value.trim()) {
			try {
				const coords = await locationService.geocodeFreeform(location.value.trim())
				finalMeetingLat = coords.lat
				finalMeetingLng = coords.lng
			} catch (geoError) {
				console.warn('Could not geocode meeting location:', geoError)
			}
		}

		const updated = await RentalService.updateRentalDetails(rentalId.value, {
			location: location.value.trim(),
			meeting_lat: finalMeetingLat,
			meeting_lng: finalMeetingLng,
			agreed_price: Number(agreedPrice.value),
			start_date: toUtcIsoString(startDate.value),
			end_date: toUtcIsoString(endDate.value),
			deleted: rental.value.deleted,
		})

		router.push({ name: 'rental_view', params: { id: updated.id } })
	} catch (e) {
		error.value = e.message || 'Failed to save rental changes.'
	} finally {
		submitting.value = false
	}
}

/**
 * Loads rental data when component is mounted.
 */
onMounted(loadData)
</script>

<template>
	<section class="max-w-3xl mx-auto">
		<h1 class="text-2xl font-bold text-gray-800 mb-6">Edit Rental Details</h1>

		<div v-if="loading" class="flex justify-center py-10">
			<fwb-spinner size="10" />
		</div>

		<div v-else class="space-y-4">
			<p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

			<form v-if="rental" class="space-y-4" @submit.prevent="saveChanges">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<fwb-input
						v-model="startDate"
						type="datetime-local"
						label="Start Date and Time"
						:min="minimumStartDate"
						required
					/>
					<fwb-input
						v-model="endDate"
						type="datetime-local"
						label="End Date and Time"
						required
					/>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Agreed Price</label>
					<input
						v-model="agreedPrice"
						type="number"
						step="0.01"
						min="0.01"
						required
						class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>
				</div>

				<rental-meeting-location-field
					v-model="location"
					v-model:meeting-lat="meetingLat"
					v-model:meeting-lng="meetingLng"
					:rental-id="rentalId"
					label="Meeting Location"
				/>

				<div class="flex items-center gap-3">
					<fwb-button color="light" type="button" @click="router.back()">Cancel</fwb-button>
					<fwb-button type="submit" :disabled="submitting">
						{{ submitting ? 'Saving...' : 'Save Changes' }}
					</fwb-button>
				</div>
			</form>
		</div>
	</section>
</template>
