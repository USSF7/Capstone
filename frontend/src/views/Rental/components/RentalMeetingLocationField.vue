<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { FwbInput, FwbSpinner } from 'flowbite-vue'
import rentalService from '../../../services/rentalService'
import userService from '../../../services/userService'
import locationService from '../../../services/locationService'
import GoogleMap from '../../../components/GoogleMap.vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  meetingLat: { type: Number, default: null },
  meetingLng: { type: Number, default: null },
  rentalId: { type: [Number, String], default: null },
  renterLat: { type: Number, default: null },
  renterLng: { type: Number, default: null },
  renterName: { type: String, default: 'Renter' },
  vendorLat: { type: Number, default: null },
  vendorLng: { type: Number, default: null },
  vendorName: { type: String, default: 'Vendor' },
  label: { type: String, default: 'Meeting Location' },
})

const emit = defineEmits(['update:modelValue', 'update:meetingLat', 'update:meetingLng'])

const locationText = ref(props.modelValue || '')
const selectedLat = ref(props.meetingLat)
const selectedLng = ref(props.meetingLng)
const loading = ref(false)
const error = ref(null)
const rental = ref(null)
const renterData = ref(null)
const vendorData = ref(null)
const suggestions = ref([])
const midpoint = ref(null)
const selectedSuggestionId = ref(null)

const hasRentalContext = computed(() => !!props.rentalId)

const renterPoint = computed(() => {
  if (renterData.value?.latitude != null && renterData.value?.longitude != null) {
    return {
      lat: renterData.value.latitude,
      lng: renterData.value.longitude,
      name: renterData.value.name || props.renterName,
    }
  }
  if (!hasRentalContext.value && props.renterLat != null && props.renterLng != null) {
    return {
      lat: props.renterLat,
      lng: props.renterLng,
      name: props.renterName,
    }
  }
  return null
})

const vendorPoint = computed(() => {
  if (vendorData.value?.latitude != null && vendorData.value?.longitude != null) {
    return {
      lat: vendorData.value.latitude,
      lng: vendorData.value.longitude,
      name: vendorData.value.name || props.vendorName,
    }
  }
  if (!hasRentalContext.value && props.vendorLat != null && props.vendorLng != null) {
    return {
      lat: props.vendorLat,
      lng: props.vendorLng,
      name: props.vendorName,
    }
  }
  return null
})

const hasMapContext = computed(() => !!(hasRentalContext.value || (renterPoint.value && vendorPoint.value)))

const hasMeetingLocation = computed(() => selectedLat.value != null && selectedLng.value != null)

const meetingPoint = computed(() =>
  hasMeetingLocation.value
    ? { lat: selectedLat.value, lng: selectedLng.value }
    : null
)

const mapCenter = computed(() => {
  if (midpoint.value) return midpoint.value
  if (meetingPoint.value) return meetingPoint.value
  if (renterPoint.value) {
    return { lat: renterPoint.value.lat, lng: renterPoint.value.lng }
  }
  if (vendorPoint.value) {
    return { lat: vendorPoint.value.lat, lng: vendorPoint.value.lng }
  }
  return { lat: 30.6295, lng: -96.3365 }
})

const mapMarkers = computed(() => {
  const marks = []

  if (renterPoint.value) {
    marks.push({
      id: 'renter',
      kind: 'party',
      lat: renterPoint.value.lat,
      lng: renterPoint.value.lng,
      title: 'Renter',
      color: '#2563EB',
      label: `<strong>Renter</strong><br>${renterPoint.value.name}`,
    })
  }

  if (vendorPoint.value) {
    marks.push({
      id: 'vendor',
      kind: 'party',
      lat: vendorPoint.value.lat,
      lng: vendorPoint.value.lng,
      title: 'Vendor',
      color: '#059669',
      label: `<strong>Vendor</strong><br>${vendorPoint.value.name}`,
    })
  }

  suggestions.value.forEach((place) => {
    const selected = selectedSuggestionId.value === place.place_id
    marks.push({
      id: place.place_id,
      kind: 'suggestion',
      lat: place.lat,
      lng: place.lng,
      title: place.name,
      color: selected ? '#DC2626' : '#D97706',
      selected,
      label: `<strong>${place.name}</strong><br>${place.address || ''}`,
      place,
    })
  })

  if (meetingPoint.value) {
    marks.push({
      id: 'meeting',
      kind: 'meeting',
      lat: meetingPoint.value.lat,
      lng: meetingPoint.value.lng,
      title: 'Selected Meeting Location',
      color: '#7C3AED',
      label: `<strong>Selected Meeting Location</strong><br>${locationText.value || ''}`,
    })
  }

  return marks
})

watch(
  () => props.modelValue,
  (value) => {
    if (value !== locationText.value) {
      locationText.value = value || ''
    }
  }
)

watch(locationText, (value) => {
  emit('update:modelValue', value)
})

watch(
  () => props.meetingLat,
  (value) => {
    if (value !== selectedLat.value) {
      selectedLat.value = value
    }
  }
)

watch(
  () => props.meetingLng,
  (value) => {
    if (value !== selectedLng.value) {
      selectedLng.value = value
    }
  }
)

watch(selectedLat, (value) => {
  emit('update:meetingLat', value)
})

watch(selectedLng, (value) => {
  emit('update:meetingLng', value)
})

async function loadRentalContext() {
  if (!hasRentalContext.value) return

  loading.value = true
  error.value = null

  try {
    rental.value = await rentalService.getRental(Number(props.rentalId))
    const [renter, vendor] = await Promise.all([
      userService.getUser(rental.value.renter_id),
      userService.getUser(rental.value.vendor_id),
    ])
    renterData.value = renter
    vendorData.value = vendor

    const suggestionData = await locationService.getMeetingSuggestions(Number(props.rentalId))
    suggestions.value = suggestionData.suggestions || []
    midpoint.value = suggestionData.midpoint || null

    if (rental.value.location && !locationText.value) {
      locationText.value = rental.value.location
    }
    if (rental.value.meeting_lat != null && rental.value.meeting_lng != null) {
      selectedLat.value = rental.value.meeting_lat
      selectedLng.value = rental.value.meeting_lng
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadPointContextSuggestions() {
  if (hasRentalContext.value) return
  if (!renterPoint.value || !vendorPoint.value) return

  loading.value = true
  error.value = null

  try {
    const suggestionData = await locationService.getMeetingSuggestionsForPoints(
      renterPoint.value.lat,
      renterPoint.value.lng,
      vendorPoint.value.lat,
      vendorPoint.value.lng
    )
    suggestions.value = suggestionData.suggestions || []
    midpoint.value = suggestionData.midpoint || null
  } catch (e) {
    error.value = e.message
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

function onLocationSelected({ rental: updatedRental }) {
  rental.value = updatedRental
  if (updatedRental?.location) {
    locationText.value = updatedRental.location
  }
}

function chooseSuggestion(place) {
  selectedSuggestionId.value = place.place_id
  const address = place.address ? `, ${place.address}` : ''
  locationText.value = `${place.name}${address}`
  selectedLat.value = place.lat
  selectedLng.value = place.lng
}

function onMapMarkerClick(marker) {
  if (marker?.kind === 'suggestion' && marker.place) {
    chooseSuggestion(marker.place)
  }
}

onMounted(async () => {
  await loadRentalContext()
  if (!hasRentalContext.value) {
    await loadPointContextSuggestions()
  }
})

watch(
  [
    () => props.renterLat,
    () => props.renterLng,
    () => props.vendorLat,
    () => props.vendorLng,
    hasRentalContext,
  ],
  () => {
    if (!hasRentalContext.value) {
      loadPointContextSuggestions()
    }
  }
)
</script>

<template>
  <div class="space-y-4">
    <fwb-input
      v-model="locationText"
      :label="label"
      placeholder="Enter meeting/pickup address"
      required
    />

    <div v-if="hasMapContext" class="rounded-lg border border-gray-200 p-4">
      <h4 class="font-medium text-gray-900 mb-3">Meeting Location Assistant</h4>

      <div v-if="loading" class="flex items-center gap-2 text-gray-500">
        <fwb-spinner size="6" />
        <span>Loading location context...</span>
      </div>

      <p v-if="error" class="text-red-600 text-sm mb-2">{{ error }}</p>

      <template v-if="!loading">
        <div v-if="hasRentalContext && rental && hasMeetingLocation" class="p-3 bg-green-50 border border-green-200 rounded mb-3">
          <p class="font-semibold text-green-800">{{ rental.location }}</p>
          <p class="text-sm text-green-600">Current meeting location</p>
        </div>

        <GoogleMap
          :center="mapCenter"
          :markers="mapMarkers"
          height="360px"
          @marker-click="onMapMarkerClick"
        />

        <div v-if="suggestions.length" class="mt-3">
          <p class="text-sm font-medium text-gray-700 mb-2">Suggested Places</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="place in suggestions"
              :key="place.place_id"
              type="button"
              class="text-xs px-3 py-1.5 rounded-full border"
              :class="selectedSuggestionId === place.place_id ? 'bg-red-50 border-red-300 text-red-700' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'"
              @click="chooseSuggestion(place)"
            >
              {{ place.name }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
