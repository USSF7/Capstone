<script setup>
import { ref, computed, onMounted } from 'vue'
import { FwbButton, FwbInput, FwbCard, FwbSpinner, FwbBadge } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import locationService from '../../services/locationService'
import GoogleMap from '../../components/GoogleMap.vue'

const auth = useAuthStore()

const nameFilter = ref('')
const radius = ref(25)
const results = ref([])
const loading = ref(false)
const error = ref(null)
const showMap = ref(false)
const searched = ref(false)

const userLat = computed(() => auth.user?.latitude)
const userLng = computed(() => auth.user?.longitude)
const hasLocation = computed(() => userLat.value != null && userLng.value != null)

const mapMarkers = computed(() =>
  results.value.map((r) => ({
    lat: r.owner_lat,
    lng: r.owner_lng,
    title: r.name,
    label: `<strong>${r.name}</strong><br>$${r.price}/day<br>${r.distance_miles} mi away`,
  }))
)

async function search() {
  if (!hasLocation.value) return
  loading.value = true
  error.value = null
  searched.value = true
  try {
    const data = await locationService.searchEquipmentNearby(
      userLat.value,
      userLng.value,
      radius.value,
      nameFilter.value || null
    )
    results.value = data.results
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (hasLocation.value) search()
})
</script>

<template>
  <section class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Find Equipment Near You</h1>

    <div v-if="!hasLocation" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <p class="text-yellow-800">
        Your location is not set. Please
        <router-link to="/profile/edit" class="underline font-medium">update your profile address</router-link>
        to search for nearby equipment.
      </p>
    </div>

    <form v-else @submit.prevent="search" class="flex flex-wrap items-end gap-4 mb-6">
      <div class="flex-1 min-w-[200px]">
        <label class="block text-sm font-medium text-gray-700 mb-1">Equipment Name</label>
        <fwb-input v-model="nameFilter" placeholder="e.g. Camera, Projector" />
      </div>
      <div class="w-32">
        <label class="block text-sm font-medium text-gray-700 mb-1">Radius (miles)</label>
        <fwb-input v-model="radius" type="number" min="1" max="500" />
      </div>
      <fwb-button type="submit" :disabled="loading">
        {{ loading ? 'Searching...' : 'Search' }}
      </fwb-button>
    </form>

    <div v-if="loading" class="flex justify-center py-8">
      <fwb-spinner size="10" />
    </div>

    <p v-if="error" class="text-red-600 text-sm mb-4">{{ error }}</p>

    <div v-if="!loading && results.length">
      <div class="flex items-center justify-between mb-4">
        <p class="text-sm text-gray-600">{{ results.length }} item{{ results.length !== 1 ? 's' : '' }} found</p>
        <fwb-button size="sm" color="light" @click="showMap = !showMap">
          {{ showMap ? 'Hide Map' : 'Show on Map' }}
        </fwb-button>
      </div>

      <GoogleMap
        v-if="showMap"
        :center="{ lat: userLat, lng: userLng }"
        :zoom="11"
        :markers="mapMarkers"
        height="350px"
        class="mb-6"
      />

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <fwb-card v-for="item in results" :key="item.id" class="p-4">
          <router-link
            :to="{ name: 'rental_create', query: { vendorId: item.owner_id, equipmentId: item.id } }"
            class="block -m-4 p-4 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div v-if="item.picture" class="mb-3">
              <img :src="item.picture" :alt="item.name" class="w-full h-32 object-cover rounded" />
            </div>
            <h3 class="font-semibold text-gray-900">{{ item.name }}</h3>
            <fwb-badge v-if="item.condition === 'Mint'" class="inline-block mt-1 mb-1" size="sm" type="default"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="item.condition === 'Above Average'" class="inline-block mt-1 mb-1" size="sm" type="green"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else-if="item.condition === 'Average'" class="inline-block mt-1 mb-1" size="sm" type="yellow"> {{ item.condition }} Condition </fwb-badge>
            <fwb-badge v-else class="inline-block mt-1 mb-1" size="sm" type="red"> {{ item.condition }} Condition </fwb-badge>
            <p class="text-sm text-gray-500 mt-1">{{ item.description }}</p>
            <p class="text-sm text-gray-700 mt-2">
              <span class="font-medium">Vendor:</span> {{ item.owner_name || 'Unknown vendor' }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Rating:</span>
              <span v-if="item.owner_rating != null">{{ item.owner_rating }}/5 ({{ item.owner_rating_count }} review{{ item.owner_rating_count === 1 ? '' : 's' }})</span>
              <span v-else>No ratings yet</span>
            </p>
            <div class="flex items-center justify-between mt-3">
              <span class="text-lg font-bold text-blue-600">${{ item.price }}/day</span>
              <span class="text-sm text-gray-500">{{ item.distance_miles }} mi away</span>
            </div>
            <p class="text-xs text-gray-400 mt-1">{{ item.owner_city }}, {{ item.owner_state }}</p>
          </router-link>
        </fwb-card>
      </div>
    </div>

    <p v-if="!loading && searched && !results.length && !error" class="text-gray-500 text-center py-8">
      No equipment found within {{ radius }} miles. Try increasing the search radius.
    </p>
  </section>
</template>
