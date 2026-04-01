<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FwbButton, FwbInput, FwbSpinner } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import EquipmentService from '../../services/equipmentService'
import RentalService from '../../services/rentalService'
import locationService from '../../services/locationService'
import RentalMeetingLocationField from './components/RentalMeetingLocationField.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const vendorId = ref(null)
const equipmentId = ref(null)

const vendor = ref(null)
const vendorEquipment = ref([])
const selectedEquipmentIds = ref([])

const agreedPrice = ref('')
const pickupLocation = ref('')
const meetingLat = ref(null)
const meetingLng = ref(null)
const startDate = ref('')
const endDate = ref('')

const loading = ref(true)
const submitting = ref(false)
const loadingEquipment = ref(false)
const error = ref('')

const userId = computed(() => auth.user?.id)
const minimumLeadTimeHours = 2
const minimumStartDate = ref('')

function pad(value) {
	return String(value).padStart(2, '0')
}

function addHours(date, hours) {
	const result = new Date(date)
	result.setHours(result.getHours() + hours)
	return result
}

function toDateTimeLocalValue(value) {
	if (!value) return ''
	const date = new Date(value)
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function fromDateTimeLocalValue(value) {
	return value ? new Date(value) : null
}

function toUtcIsoString(value) {
	if (!value) return ''
	return new Date(value).toISOString()
}

function parsePositiveInt(value) {
	const parsed = Number.parseInt(value, 10)
	return Number.isInteger(parsed) && parsed > 0 ? parsed : null
}

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
		const earliestStart = addHours(today, minimumLeadTimeHours + 1)
		const defaultEnd = addHours(earliestStart, 24)
		minimumStartDate.value = toDateTimeLocalValue(earliestStart)
		startDate.value = minimumStartDate.value
		endDate.value = toDateTimeLocalValue(defaultEnd)

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

function onDateChange() {
	error.value = ''
	if (startDate.value && endDate.value) {
		loadEquipmentAvailability()
	}
}

function toggleEquipmentSelection(equipment) {
	if (!equipment.available) return

	const index = selectedEquipmentIds.value.indexOf(equipment.id)
	if (index >= 0) {
		selectedEquipmentIds.value.splice(index, 1)
	} else {
		selectedEquipmentIds.value.push(equipment.id)
	}
}

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
					<fwb-input
						v-model="startDate"
						type="datetime-local"
						label="Start Date and Time"
						:min="minimumStartDate"
						required
						@change="onDateChange"
					/>
					<fwb-input
						v-model="endDate"
						type="datetime-local"
						label="End Date and Time"
						required
						@change="onDateChange"
					/>
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
