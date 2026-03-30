<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { FwbSpinner, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import rentalService from '../../services/rentalService'
import userService from '../../services/userService'
import MeetingLocationPicker from '../../components/MeetingLocationPicker.vue'
import GoogleMap from '../../components/GoogleMap.vue'

const route = useRoute()
const auth = useAuthStore()

const rentalId = computed(() => Number(route.params.id))
const rental = ref(null)
const renterData = ref(null)
const vendorData = ref(null)
const loading = ref(true)
const error = ref(null)

const hasMeetingLocation = computed(
  () => rental.value?.meeting_lat != null && rental.value?.meeting_lng != null
)

const currentUserId = computed(() => auth.user?.id)
const isRenter = computed(() => currentUserId.value === rental.value?.renter_id)

const meetingPoint = computed(() =>
  hasMeetingLocation.value
    ? { lat: rental.value.meeting_lat, lng: rental.value.meeting_lng }
    : null
)

const userOrigin = computed(() => {
  const user = isRenter.value ? renterData.value : vendorData.value
  if (user?.latitude && user?.longitude) {
    return { lat: user.latitude, lng: user.longitude }
  }
  return null
})

const mapMarkers = computed(() => {
  if (!meetingPoint.value) return []
  const marks = [
    { lat: meetingPoint.value.lat, lng: meetingPoint.value.lng, title: 'Meeting Point' },
  ]
  if (renterData.value?.latitude) {
    marks.push({ lat: renterData.value.latitude, lng: renterData.value.longitude, title: 'Renter' })
  }
  if (vendorData.value?.latitude) {
    marks.push({ lat: vendorData.value.latitude, lng: vendorData.value.longitude, title: 'Vendor' })
  }
  return marks
})

async function loadData() {
  try {
    rental.value = await rentalService.getRental(rentalId.value)
    const [renter, vendor] = await Promise.all([
      userService.getUser(rental.value.renter_id),
      userService.getUser(rental.value.vendor_id),
    ])
    renterData.value = renter
    vendorData.value = vendor
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function onLocationSelected({ rental: updatedRental }) {
  rental.value = updatedRental
}

onMounted(loadData)
</script>

<template>
  <section class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Meeting Location</h1>

    <div v-if="loading" class="flex justify-center py-8">
      <fwb-spinner size="10" />
    </div>

    <p v-if="error" class="text-red-600 text-sm mb-4">{{ error }}</p>

    <template v-if="!loading && rental">
      <!-- No meeting location set: show picker -->
      <div v-if="!hasMeetingLocation">
        <MeetingLocationPicker
          :rental-id="rentalId"
          @location-selected="onLocationSelected"
        />
      </div>

      <!-- Meeting location set: show map with directions -->
      <div v-else>
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h2 class="font-semibold text-green-800">{{ rental.location }}</h2>
          <p class="text-sm text-green-600 mt-1">Meeting location confirmed</p>
        </div>

        <GoogleMap
          :center="meetingPoint"
          :markers="mapMarkers"
          :show-directions="!!userOrigin"
          :origin="userOrigin"
          :destination="meetingPoint"
          height="500px"
          class="mb-6"
        />

        <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
          <div class="p-3 bg-gray-50 rounded">
            <p class="font-medium text-gray-800">Renter</p>
            <p>{{ renterData?.name }} - {{ renterData?.city }}, {{ renterData?.state }}</p>
          </div>
          <div class="p-3 bg-gray-50 rounded">
            <p class="font-medium text-gray-800">Vendor</p>
            <p>{{ vendorData?.name }} - {{ vendorData?.city }}, {{ vendorData?.state }}</p>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
