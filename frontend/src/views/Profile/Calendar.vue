<template>
	<section class="space-y-6">
		<div class="rounded-2xl bg-gradient-to-r from-sky-700 via-cyan-600 to-emerald-600 p-6 text-white shadow-lg">
			<p class="text-sm font-semibold uppercase tracking-wider text-cyan-100">My Schedule</p>
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
				<span class="inline-flex items-center gap-2 rounded-full bg-sky-100 px-3 py-1 font-medium text-sky-700">
					<span class="h-2 w-2 rounded-full bg-sky-600"></span> Event
				</span>
				<span class="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-700">
					<span class="h-2 w-2 rounded-full bg-emerald-600"></span> Rental
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
							:class="day.isToday ? 'bg-cyan-600 text-white' : day.inCurrentMonth ? 'text-slate-800' : 'text-slate-400'"
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
							:key="`${day.isoKey}-${item.type}-${item.id}`"
							:to="item.route"
							class="block truncate rounded-md px-2 py-1 text-xs font-medium transition hover:brightness-95"
							:class="item.type === 'event' ? 'bg-sky-100 text-sky-800' : 'bg-emerald-100 text-emerald-800'"
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
import { computed, onMounted, ref } from 'vue'
import eventService from '../../services/eventService'
import rentalService from '../../services/rentalService'

// TODO: Replace with authenticated user id when auth module is integrated.
const USER_ID = 10

const loading = ref(true)
const error = ref('')
const events = ref([])
const rentals = ref([])
const rentalsWithoutEvent = ref([])
const currentMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function parseDateString(dateString) {
	const [year, month, day] = dateString.split('T')[0].split('-').map(Number)
	return new Date(year, month - 1, day)
}

function getIsoDate(date) {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

function addDays(date, days) {
	const d = new Date(date)
	d.setDate(d.getDate() + days)
	return d
}

async function loadCalendarData() {
	loading.value = true
	error.value = ''

	try {
		const [eventsData, renterRentals, vendorRentals] = await Promise.all([
			eventService.getEventsByUser(USER_ID),
			rentalService.getRentalsByRenter(USER_ID),
			rentalService.getRentalsByVendor(USER_ID)
		])

		events.value = eventsData

		const rentalMap = new Map()
		for (const rental of [...renterRentals, ...vendorRentals]) {
			if (!rentalMap.has(rental.id)) {
				rentalMap.set(rental.id, rental)
			}
		}

		rentals.value = Array.from(rentalMap.values())
		rentalsWithoutEvent.value = rentals.value.filter(rental => rental.event_id == null)
	} catch (err) {
		error.value = err.message || 'Failed to load calendar data'
	} finally {
		loading.value = false
	}
}

const rentalsByEventId = computed(() => {
	const map = {}

	for (const rental of rentals.value) {
		if (rental.event_id == null) continue
		if (!map[rental.event_id]) map[rental.event_id] = []
		map[rental.event_id].push(rental)
	}

	return map
})

const itemsByDate = computed(() => {
	const map = {}
	const maxVisibleItems = 3

	for (const event of events.value) {
		const eventDate = parseDateString(event.date)
		const key = getIsoDate(eventDate)
		if (!map[key]) map[key] = []

		map[key].push({
			id: event.id,
			type: 'event',
			title: event.name,
			description: `${event.name} (Event)`,
			route: { name: 'events-view', params: { id: event.id } }
		})
	}

	for (const rental of rentalsWithoutEvent.value) {
		const start = parseDateString(rental.start_date)
		const end = parseDateString(rental.end_date)

		for (let d = new Date(start); d <= end; d = addDays(d, 1)) {
			const key = getIsoDate(d)
			if (!map[key]) map[key] = []

			map[key].push({
				id: rental.id,
				type: 'rental',
				title: `Rental #${rental.id}`,
				description: `Rental #${rental.id} (${rental.status}) at ${rental.location || 'No location'}`,
				route: { name: 'rentals-view', params: { id: rental.id } }
			})
		}
	}

	for (const event of events.value) {
		const eventDate = parseDateString(event.date)
		const key = getIsoDate(eventDate)
		if (!map[key]) continue

		const eventRentals = rentalsByEventId.value[event.id] || []
		if (map[key].length >= maxVisibleItems || eventRentals.length === 0) {
			continue
		}

		for (const rental of eventRentals) {
			if (map[key].length >= maxVisibleItems) {
				break
			}

			map[key].push({
				id: rental.id,
				type: 'rental',
				title: `Rental #${rental.id} (Event)`,
				description: `Rental #${rental.id} for ${event.name} (${rental.status})`,
				route: { name: 'rentals-view', params: { id: rental.id } }
			})
		}
	}

	return map
})

const monthLabel = computed(() => {
	return currentMonth.value.toLocaleDateString('en-US', {
		month: 'long',
		year: 'numeric'
	})
})

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

function goToPreviousMonth() {
	currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
}

function goToNextMonth() {
	currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
}

function goToToday() {
	const now = new Date()
	currentMonth.value = new Date(now.getFullYear(), now.getMonth(), 1)
}

onMounted(loadCalendarData)
</script>