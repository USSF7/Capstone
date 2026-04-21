<template>
	<section class="space-y-6">
		<div class="rounded-2xl bg-gradient-to-r from-sky-700 via-cyan-600 to-emerald-600 p-6 text-white shadow-lg">
			<h1 class="text-sm font-semibold tracking-wider text-cyan-100">My Schedule</h1>
		</div>

		<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
			<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
				<h2 class="text-2xl font-semibold text-slate-900">{{ monthLabel }}</h2>
				<div class="flex items-center gap-2">
					<button
						class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
						@click="goToPreviousMonth"
					>
						Previous
					</button>
					<button
						class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
						@click="goToToday"
					>
						Today
					</button>
					<button
						class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
						@click="goToNextMonth"
					>
						Next
					</button>
				</div>
			</div>

			<div class="mt-4 flex flex-wrap items-center gap-3 text-xs">
				<span class="inline-flex items-center gap-2 rounded-full bg-amber-100 px-3 py-1 font-medium text-amber-700">
					<span class="h-2 w-2 rounded-full bg-amber-500"></span> Requesting
				</span>
				<span class="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-700">
					<span class="h-2 w-2 rounded-full bg-emerald-600"></span> Active
				</span>
				<span class="inline-flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 font-medium text-blue-700">
					<span class="h-2 w-2 rounded-full bg-blue-600"></span> Returned
				</span>
				<span class="inline-flex items-center gap-2 rounded-full bg-red-100 px-3 py-1 font-medium text-red-700">
					<span class="h-2 w-2 rounded-full bg-red-600"></span> Disputed
				</span>
			</div>
		</div>

		<p v-if="loading" class="rounded-xl border border-slate-200 bg-white p-4 text-slate-600 shadow-sm">
			Loading calendar items...
		</p>
		<p v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 shadow-sm">
			{{ error }}
		</p>

		<div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
			<div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50">
				<div
					v-for="weekday in weekDays"
					:key="weekday"
					class="px-2 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-600"
				>
					{{ weekday }}
				</div>
			</div>

			<div class="grid grid-cols-7">
				<div
					v-for="day in calendarDays"
					:key="day.isoKey"
					class="min-h-[130px] border-b border-r border-slate-200 p-2"
					:class="day.inCurrentMonth ? 'bg-white' : 'bg-slate-50'"
				>
					<div class="mb-2 flex items-center justify-between">
						<span
							class="inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold"
							:class="day.isToday ? 'bg-cyan-800 text-white' : day.inCurrentMonth ? 'text-slate-800' : 'text-slate-600'"
						>
							{{ day.date.getDate() }}
						</span>
						<span v-if="day.items.length" class="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
							{{ day.items.length }} item{{ day.items.length === 1 ? '' : 's' }}
						</span>
					</div>

					<div class="space-y-1">
						<router-link
							v-for="item in day.items.slice(0, 3)"
							:key="`${day.isoKey}-${item.id}`"
							:to="{ name: 'rental_view', params: { id: item.id } }"
							class="block truncate rounded-md px-2 py-1 text-xs font-medium transition-colors hover:brightness-95"
							:class="getStatusClasses(item.status)"
							:title="item.description"
						>
							{{ item.title }}
						</router-link>
						<div
							v-if="day.items.length > 3"
							class="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600"
						>
							+{{ day.items.length - 3 }} more
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>
</template>

<script setup>
/**
 * The calendar view that displays upcoming and previous rentals
 * @module ProfileCalendar
 */

import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import rentalService from '../../services/rentalService'

/**
 * Auth store providing current logged-in user.
 */
const auth = useAuthStore()

/**
 * Current authenticated user ID (reactive).
 */
const USER_ID = computed(() => auth.user?.id)

/**
 * Loading state for calendar data fetch.
 */
const loading = ref(true)

/**
 * Error message for failed data loading.
 */
const error = ref('')

/**
 * List of rentals.
 */
const rentals = ref([])

/**
 * Currently displayed month (always set to first day of month).
 */
const currentMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))

/**
 * Weekday labels used in calendar header row.
 */
const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

/**
 * Parses backend ISO date string into local Date object.
 *
 * @param {string} dateString - ISO date string
 * @returns {Date} The date in a Date object
 */
function parseDateString(dateString) {
	const [year, month, day] = dateString.split('T')[0].split('-').map(Number)
	return new Date(year, month - 1, day)
}

/**
 * Converts Date object into ISO date key (YYYY-MM-DD).
 *
 * @param {Date} date The date in a Date object.
 * @returns {string} Formatted date in the format of YYYY-MM-DD.
 */
function getIsoDate(date) {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

/**
 * Returns a new Date offset by a number of days.
 *
 * @param {Date} date The date in a Date object.
 * @param {number} days The number of days.
 * @returns {Date} The offset date in a Date object
 */
function addDays(date, days) {
	const d = new Date(date)
	d.setDate(d.getDate() + days)
	return d
}

/**
 * Maps rental status to Tailwind CSS styling classes.
 * Used to visually distinguish calendar items.
 *
 * @param {string} status The current status of a rental.
 * @returns {string} The CSS styling class.
 */
function getStatusClasses(status) {
	switch (status) {
		case 'requesting':
			return 'bg-amber-100 text-amber-800'
		case 'active':
			return 'bg-emerald-100 text-emerald-800'
		case 'returned':
			return 'bg-blue-100 text-blue-800'
		case 'disputed':
		case 'denied':
		case 'cancelled':
			return 'bg-red-100 text-red-800'
		default:
			return 'bg-slate-100 text-slate-800'
	}
}

/**
 * Loads calendar-related rental data for the current user.
 */
async function loadCalendarData() {
	loading.value = true
	error.value = ''

	try {
		const [renterRentals, vendorRentals] = await Promise.all([
			rentalService.getRentalsByRenter(USER_ID.value),
			rentalService.getRentalsByVendor(USER_ID.value)
		])

		const rentalMap = new Map()
		for (const rental of [...renterRentals, ...vendorRentals]) {
			if (!rentalMap.has(rental.id)) {
				rentalMap.set(rental.id, rental)
			}
		}

		rentals.value = Array.from(rentalMap.values())
	} catch (err) {
		error.value = err.message || 'Failed to load calendar data'
	} finally {
		loading.value = false
	}
}

/**
 * Computed map of rentals grouped by date.
 */
const itemsByDate = computed(() => {
	const map = {}

	for (const rental of rentals.value) {
		if (rental.status === 'cancelled' || rental.status === 'denied') {
			continue
		}

		const start = parseDateString(rental.start_date)
		const end = parseDateString(rental.end_date)

		for (let d = new Date(start); d <= end; d = addDays(d, 1)) {
			const key = getIsoDate(d)
			if (!map[key]) map[key] = []

			map[key].push({
				id: rental.id,
				title: `Rental #${rental.id}`,
				status: rental.status,
				description: `Rental #${rental.id} (${rental.status}) at ${rental.location || 'No location'}`
			})
		}
	}

	return map
})

/**
 * Human-readable label for current calendar month.
 */
const monthLabel = computed(() => {
	return currentMonth.value.toLocaleDateString('en-US', {
		month: 'long',
		year: 'numeric'
	})
})

/**
 * Generates full calendar grid including leading and trailing days.
 */
const calendarDays = computed(() => {
	const year = currentMonth.value.getFullYear()
	const month = currentMonth.value.getMonth()

	const firstOfMonth = new Date(year, month, 1)
	const firstWeekDay = firstOfMonth.getDay()
	const daysInMonth = new Date(year, month + 1, 0).getDate()
	const daysInPrevMonth = new Date(year, month, 0).getDate()

	const today = new Date()
	const todayKey = getIsoDate(today)

	const days = []

	for (let i = firstWeekDay - 1; i >= 0; i--) {
		const date = new Date(year, month - 1, daysInPrevMonth - i)
		const key = getIsoDate(date)
		days.push({
			date,
			isoKey: key,
			inCurrentMonth: false,
			isToday: key === todayKey,
			items: itemsByDate.value[key] || []
		})
	}

	for (let day = 1; day <= daysInMonth; day++) {
		const date = new Date(year, month, day)
		const key = getIsoDate(date)
		days.push({
			date,
			isoKey: key,
			inCurrentMonth: true,
			isToday: key === todayKey,
			items: itemsByDate.value[key] || []
		})
	}

	while (days.length % 7 !== 0) {
		const offset = days.length - (firstWeekDay + daysInMonth)
		const date = new Date(year, month + 1, offset + 1)
		const key = getIsoDate(date)
		days.push({
			date,
			isoKey: key,
			inCurrentMonth: false,
			isToday: key === todayKey,
			items: itemsByDate.value[key] || []
		})
	}

	return days
})

/**
 * Navigate calendar to previous month.
 */
function goToPreviousMonth() {
	currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
}

/**
 * Navigate calendar to next month.
 */
function goToNextMonth() {
	currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
}

/**
 * Reset calendar view to current month.
 */
function goToToday() {
	const now = new Date()
	currentMonth.value = new Date(now.getFullYear(), now.getMonth(), 1)
}

/**
 * Loads calendar data on component mount.
 */
onMounted(loadCalendarData)
</script>