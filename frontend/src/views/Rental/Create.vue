<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbButton, FwbSpinner } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import EquipmentService from '../../services/equipmentService'
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
 * Auth store providing current logged-in user.
 */
const auth = useAuthStore()

/**
 * Vendor ID to identify vendor.
 */
const vendorId = ref(null)

/**
 * Equipment ID to identify equipment.
 */
const equipmentId = ref(null)

/**
 * Vendor information
 */
const vendor = ref(null)

/**
 * All of vendor's equipment
 */
const vendorEquipment = ref([])

/**
 * Selected equipment IDs
 */
const selectedEquipmentIds = ref([])

/**
 * Form input agreed price
 */
const agreedPrice = ref('')

/**
 * Form input pickup location
 */
const pickupLocation = ref('')

/**
 * Latitude Coordinate for pickup location
 */
const meetingLat = ref(null)

/**
 * Longitude Coordinate for pickup location
 */
const meetingLng = ref(null)

/**
 * Start date
 */
const startDate = ref('')

/**
 * End date
 */
const endDate = ref('')

/**
 * Form input start date
 */
const startDatePart = ref('')

/**
 * Form input start time
 */
const startTimePart = ref('')

/**
 * Form input end date
 */
const endDatePart = ref('')

/**
 * Form input end time
 */
const endTimePart = ref('')

/**
 * Loading state
 */
const loading = ref(true)

/**
 * Submitting state
 */
const submitting = ref(false)

/**
 * Loading equipment state
 */
const loadingEquipment = ref(false)

/**
 * Error message in the user interface
 */
const error = ref('')

/**
 * Current authenticated user ID
 */
const userId = computed(() => auth.user?.id)

/**
 * Minimum lead time before rental start (hours)
 */
const minimumLeadTimeHours = 2

/**
 * Earliest valid start datetime
 */
const minimumStartDate = ref('')

/**
 * All valid 15-minute time slots in a day
 */
const quarterHourTimes = Array.from({ length: 96 }, (_, index) => {
	const hours = Math.floor(index / 4)
	const minutes = (index % 4) * 15
	return `${pad(hours)}:${pad(minutes)}`
})

/**
 * Pads a numeric value to two digits
 * @param {number} value The current value
 * @returns {string} The padded value with two digits
 */
function pad(value) {
	return String(value).padStart(2, '0')
}

/**
 * Adds hours to a Date object
 * @param {Date} date The inputted date
 * @param {number} hours The inputted hours
 * @returns {Date} The new date object with the added hours
 */
function addHours(date, hours) {
	const result = new Date(date)
	result.setHours(result.getHours() + hours)
	return result
}

/**
 * Rounds a date up to the next 15-minute interval
 * @param {Date} date The inputted date
 * @returns {Date} The date rounded up to the next quarter hour
 */
function roundUpToNextQuarterHour(date) {
	const result = new Date(date)
	result.setSeconds(0, 0)
	const minutes = result.getMinutes()
	const remainder = minutes % 15

	if (remainder !== 0) {
		result.setMinutes(minutes + (15 - remainder))
	}

	return result
}

/**
 * Converts datetime-local string to input format
 * @param {Date|string} value The inputted date
 * @returns {string} The date in input format
 */
function toDateTimeLocalValue(value) {
	if (!value) return ''
	const date = new Date(value)
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

/**
 * Parses datetime-local string into Date
 * @param {string} value The inputted date
 * @returns {Date|null} Date parsed into a Date object
 */
function fromDateTimeLocalValue(value) {
	return value ? new Date(value) : null
}

/**
 * Converts a datetime-local string into the nearest valid 15-minute increment.
 *
 * @param {string} value - A datetime-local string
 * @returns {string} A normalized datetime-local string rounded up to the next 15-minute interval
 */
function normalizeDateTimeLocalToQuarterHour(value) {
	const date = fromDateTimeLocalValue(value)
	if (!date) return ''
	return toDateTimeLocalValue(roundUpToNextQuarterHour(date))
}

/**
 * Checks whether a datetime-local string is already aligned to a 15-minute increment.
 *
 * @param {string} value - A datetime-local string
 * @returns {boolean} True if the time is exactly on a quarter-hour boundary, otherwise false.
 */
function isQuarterHourValue(value) {
	const date = fromDateTimeLocalValue(value)
	if (!date) return false
	return date.getMinutes() % 15 === 0 && date.getSeconds() === 0
}

/**
 * Converts a datetime-local value into an ISO 8601 UTC string.
 *
 * @param {string} value - A datetime-local string.
 * @returns {string} ISO string in UTC format, or empty string if input is false.
 */
function toUtcIsoString(value) {
	if (!value) return ''
	return new Date(value).toISOString()
}

/**
 * Extracts the date portion (YYYY-MM-DD) from a datetime-local string.
 *
 * @param {string} value - A datetime-local string.
 * @returns {string} The date portion of the string, or empty string if invalid.
 */
function getDatePart(value) {
	return value?.split('T')[0] || ''
}

/**
 * Extracts the time portion (HH:mm) from a datetime-local string.
 *
 * @param {string} value - A datetime-local string.
 * @returns {string} The time portion (24-hour format), or empty string if invalid.
 */
function getTimePart(value) {
	return value?.split('T')[1]?.slice(0, 5) || ''
}

/**
 * Combines separate date and time strings into a single datetime-local string.
 *
 * @param {string} datePart - Date string in YYYY-MM-DD format.
 * @param {string} timePart - Time string in HH:mm format.
 * @returns {string} Combined datetime-local string or empty string if inputs are incomplete.
 */
function combineDateTimeLocal(datePart, timePart) {
	if (!datePart || !timePart) return ''
	return `${datePart}T${timePart}`
}

/**
 * Formats a 24-hour time string into a human-readable 12-hour format.
 *
 * @param {string} time24 - Time in 24-hour format (HH:mm)
 * @returns {string} Formatted 12-hour time string, or original value if parsing fails.
 */
function formatTime12Hour(time24) {
	if (!time24) return ''
	const [hourPart, minutePart] = time24.split(':')
	const hour = Number(hourPart)
	if (!Number.isFinite(hour)) return time24

	const period = hour >= 12 ? 'PM' : 'AM'
	const hour12 = hour % 12 === 0 ? 12 : hour % 12
	return `${hour12}:${minutePart} ${period}`
}

/**
 * Safely parses a value into a strictly positive integer.
 *
 * @param {string|number} value - Input value to parse.
 * @returns {number|null} A positive integer if valid, otherwise null.
 */
function parsePositiveInt(value) {
	const parsed = Number.parseInt(value, 10)
	return Number.isInteger(parsed) && parsed > 0 ? parsed : null
}

/**
 * Extracts the date portion (YYYY-MM-DD) from the minimum allowed start datetime.
 */
const minimumStartDatePart = computed(() => getDatePart(minimumStartDate.value))

/**
 * Extracts the time portion (HH:mm) from the minimum allowed start datetime.
 */
const minimumStartTimePart = computed(() => getTimePart(minimumStartDate.value))

/**
 * Generates valid selectable start-time options based on the selected start date.
 *
 * @returns {ComputedRef<string[]>} Array of valid HH:mm time strings for start time selection.
 */
const startTimeOptions = computed(() => {
	if (!startDatePart.value || startDatePart.value !== minimumStartDatePart.value) {
		return quarterHourTimes
	}

	return quarterHourTimes.filter((time) => time >= minimumStartTimePart.value)
})

/**
 * Generates valid selectable end-time options based on the selected start/end dates.
 *
 * @returns {ComputedRef<string[]>} Array of valid HH:mm time strings for end time selection.
 */
const endTimeOptions = computed(() => {
	if (!endDatePart.value || !startDatePart.value || !startTimePart.value) {
		return quarterHourTimes
	}

	if (endDatePart.value !== startDatePart.value) {
		return quarterHourTimes
	}

	return quarterHourTimes.filter((time) => time > startTimePart.value)
})

/**
 * Syncs split date/time UI fields with their combined datetime-local representations.
 */
function syncDatePartsFromValues() {
	startDatePart.value = getDatePart(startDate.value)
	startTimePart.value = getTimePart(startDate.value)
	endDatePart.value = getDatePart(endDate.value)
	endTimePart.value = getTimePart(endDate.value)
}

/**
 * Loads initial rental creation context including vendor data, default times,
 * and initial pickup location.
 */
async function loadContext() {
	try {
		error.value = ''

		// Accept common query param variants for deep links.
		vendorId.value = parsePositiveInt(
			route.query.vendorId ?? route.query.vendor_id ?? route.params.vendorId
		)
		equipmentId.value = parsePositiveInt(
			route.query.equipmentId ?? route.query.equipment_id
		)

		if (!vendorId.value) {
			error.value = 'No vendor was provided. Start from an equipment listing to create a request.'
			return
		}

		vendor.value = await UserService.getUser(vendorId.value)
		if (!vendor.value?.vendor) {
			error.value = 'Selected user is not a vendor.'
			return
		}


		const today = new Date()
		const earliestStart = roundUpToNextQuarterHour(addHours(today, minimumLeadTimeHours + 1))
		const defaultEnd = addHours(earliestStart, 24)
		minimumStartDate.value = toDateTimeLocalValue(earliestStart)
		startDate.value = minimumStartDate.value
		endDate.value = toDateTimeLocalValue(defaultEnd)
		syncDatePartsFromValues()

		pickupLocation.value = [auth.user?.street_address, auth.user?.city, auth.user?.state, auth.user?.zip_code]
			.filter(Boolean)
			.join(', ')

		await loadEquipmentAvailability()
	} catch (e) {
		error.value = e.message || 'Failed to load rental request context.'
	} finally {
		loading.value = false
	}
}

/**
 * Fetches vendor equipment availability for the selected time range.
 */
async function loadEquipmentAvailability() {
	if (!vendorId.value || !startDate.value || !endDate.value) return

	try {
		loadingEquipment.value = true
		const response = await RentalService.getVendorEquipmentAvailability(
			vendorId.value,
			toUtcIsoString(startDate.value),
			toUtcIsoString(endDate.value)
		)
		vendorEquipment.value = response.equipment || []

		const availableIds = new Set(vendorEquipment.value.filter((item) => item.available).map((item) => item.id))
		selectedEquipmentIds.value = selectedEquipmentIds.value.filter((id) => availableIds.has(id))

		if (equipmentId.value) {
			const initialItem = vendorEquipment.value.find((item) => item.id === equipmentId.value)
			if (initialItem && initialItem.available && !selectedEquipmentIds.value.includes(initialItem.id)) {
				selectedEquipmentIds.value.push(initialItem.id)
			}
		}
	} catch (e) {
		error.value = e.message || 'Failed to load equipment availability.'
	} finally {
		loadingEquipment.value = false
	}
}

/**
 * Handles user changes to date or time inputs.
 */
function onDateChange() {
	error.value = ''

	if (startDatePart.value && !startTimeOptions.value.includes(startTimePart.value)) {
		startTimePart.value = startTimeOptions.value[0] || ''
	}

	if (endDatePart.value && !endTimeOptions.value.includes(endTimePart.value)) {
		endTimePart.value = endTimeOptions.value[0] || ''
	}

	startDate.value = combineDateTimeLocal(startDatePart.value, startTimePart.value)
	endDate.value = combineDateTimeLocal(endDatePart.value, endTimePart.value)

	if (startDate.value && endDate.value) {
		loadEquipmentAvailability()
	}
}

/**
 * Toggles selection state of a vendor equipment item.
 *
 * @param {Object} equipment - Equipment object from vendor list.
 * @param {number} equipment.id - Unique equipment identifier.
 * @param {boolean} equipment.available - Whether item can be selected.
 */
function toggleEquipmentSelection(equipment) {
	if (!equipment.available) return

	const index = selectedEquipmentIds.value.indexOf(equipment.id)
	if (index >= 0) {
		selectedEquipmentIds.value.splice(index, 1)
	} else {
		selectedEquipmentIds.value.push(equipment.id)
	}
}

/**
 * Submits a rental request to the backend.
 */
async function submitRequest() {
	if (!userId.value) {
		error.value = 'You must be logged in.'
		return
	}

	if (!vendorId.value) {
		error.value = 'Vendor is required.'
		return
	}

	if (!agreedPrice.value || Number(agreedPrice.value) <= 0) {
		error.value = 'Offer price must be greater than 0.'
		return
	}

	if (!startDate.value || !endDate.value) {
		error.value = 'Start and end dates are required.'
		return
	}

	startDate.value = normalizeDateTimeLocalToQuarterHour(startDate.value)
	endDate.value = normalizeDateTimeLocalToQuarterHour(endDate.value)
	syncDatePartsFromValues()

	if (!isQuarterHourValue(startDate.value) || !isQuarterHourValue(endDate.value)) {
		error.value = 'Please select times in 15-minute increments.'
		return
	}

	if (minimumStartDate.value && fromDateTimeLocalValue(startDate.value) < fromDateTimeLocalValue(minimumStartDate.value)) {
		error.value = 'Start date must be at least 2 hours in the future.'
		return
	}

	if (new Date(endDate.value) <= new Date(startDate.value)) {
		error.value = 'End date must be after start date.'
		return
	}

	if (!pickupLocation.value?.trim()) {
		error.value = 'Pickup location is required.'
		return
	}

	if (!selectedEquipmentIds.value.length) {
		error.value = 'Select at least one available equipment item.'
		return
	}

	try {
		submitting.value = true
		error.value = ''

		let finalMeetingLat = meetingLat.value
		let finalMeetingLng = meetingLng.value
		if ((finalMeetingLat == null || finalMeetingLng == null) && pickupLocation.value.trim()) {
			try {
				const coords = await locationService.geocodeFreeform(pickupLocation.value.trim())
				finalMeetingLat = coords.lat
				finalMeetingLng = coords.lng
			} catch (geoError) {
				// Keep flow functional even if geocoding fails.
				console.warn('Could not geocode meeting location:', geoError)
			}
		}

		const rental = await RentalService.createRentalRequestWithEquipment(
			vendorId.value,
			Number(agreedPrice.value),
			toUtcIsoString(startDate.value),
			toUtcIsoString(endDate.value),
			pickupLocation.value.trim(),
			selectedEquipmentIds.value,
			finalMeetingLat,
			finalMeetingLng
		)

		router.push({ name: 'rental_view', params: { id: rental.id } })
	} catch (e) {
		error.value = e.message || 'Failed to create rental request.'
	} finally {
		submitting.value = false
	}
}

onMounted(loadContext)
</script>

<template>
	<section class="max-w-2xl mx-auto">
		<h1 class="text-2xl font-bold text-gray-800 mb-6">Create Rental Request</h1>

		<div v-if="loading" class="flex justify-center py-12">
			<fwb-spinner size="10" />
		</div>

		<div v-else class="space-y-4">
			<p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

			<div v-if="vendor" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
				<p class="text-sm text-gray-600">Vendor</p>
				<p class="font-semibold text-gray-900">{{ vendor.name }}</p>
			</div>

			<form class="space-y-4" @submit.prevent="submitRequest">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Start Date and Time</label>
						<div class="grid grid-cols-2 gap-2">
							<input
								v-model="startDatePart"
								type="date"
								:min="minimumStartDatePart"
								required
								class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								@change="onDateChange"
							/>
							<select
								v-model="startTimePart"
								required
								class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								@change="onDateChange"
							>
								<option v-for="time in startTimeOptions" :key="`start-${time}`" :value="time">{{ formatTime12Hour(time) }}</option>
							</select>
						</div>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">End Date and Time</label>
						<div class="grid grid-cols-2 gap-2">
							<input
								v-model="endDatePart"
								type="date"
								:min="startDatePart || minimumStartDatePart"
								required
								class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								@change="onDateChange"
							/>
							<select
								v-model="endTimePart"
								required
								class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								@change="onDateChange"
							>
								<option v-for="time in endTimeOptions" :key="`end-${time}`" :value="time">{{ formatTime12Hour(time) }}</option>
							</select>
						</div>
					</div>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Offer Price</label>
					<input
						v-model="agreedPrice"
						type="number"
						step="0.01"
						min="0.01"
						placeholder="Enter your offer amount"
						required
						class="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>
				</div>

				<rental-meeting-location-field
					v-model="pickupLocation"
					v-model:meeting-lat="meetingLat"
					v-model:meeting-lng="meetingLng"
					:renter-lat="auth.user?.latitude"
					:renter-lng="auth.user?.longitude"
					:renter-name="auth.user?.name || 'Renter'"
					:vendor-lat="vendor?.latitude"
					:vendor-lng="vendor?.longitude"
					:vendor-name="vendor?.name || 'Vendor'"
					label="Pickup Location"
				/>

				<div class="rounded-lg border border-gray-200 p-4">
					<p class="font-medium text-gray-900 mb-3">Vendor Equipment</p>
					<p class="text-sm text-gray-500 mb-3">
						Unavailable items are shown for visibility and cannot be selected.
					</p>

					<div v-if="loadingEquipment" class="py-4">
						<fwb-spinner size="6" />
					</div>

					<div v-else-if="!vendorEquipment.length" class="text-sm text-gray-500">
						This vendor has no equipment listed.
					</div>

					<div v-else class="space-y-2 max-h-72 overflow-y-auto">
						<label
							v-for="item in vendorEquipment"
							:key="item.id"
							class="flex items-start gap-3 p-3 rounded border"
							:class="item.available ? 'bg-white border-gray-200 cursor-pointer' : 'bg-gray-100 border-gray-200 cursor-not-allowed opacity-80'"
						>
							<input
								type="checkbox"
								:checked="selectedEquipmentIds.includes(item.id)"
								:disabled="!item.available"
								@change="toggleEquipmentSelection(item)"
							/>
							<div class="flex-1">
								<div class="flex items-center justify-between gap-2">
									<p class="font-medium text-gray-900">{{ item.name }}</p>
									<span class="text-sm font-semibold text-gray-700">${{ item.price }}</span>
								</div>
								<p class="text-sm text-gray-500" v-if="item.description">{{ item.description }}</p>
								<p v-if="!item.available" class="text-xs text-red-600 mt-1">{{ item.unavailable_reason }}</p>
							</div>
						</label>
					</div>
				</div>

				<div class="flex items-center gap-3">
					<fwb-button color="light" @click="router.back()" type="button">Cancel</fwb-button>
					<fwb-button type="submit" :disabled="submitting || !vendorId || loadingEquipment">
						{{ submitting ? 'Submitting...' : 'Create Request' }}
					</fwb-button>
				</div>
			</form>
		</div>
	</section>
</template>
