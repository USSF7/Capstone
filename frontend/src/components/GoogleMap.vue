<script setup>
import { ref, onMounted, watch, toRefs } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'
import locationService from '../services/locationService'

const props = defineProps({
  center: { type: Object, required: true },
  zoom: { type: Number, default: 13 },
  markers: { type: Array, default: () => [] },
  showDirections: { type: Boolean, default: false },
  origin: { type: Object, default: null },
  destination: { type: Object, default: null },
  height: { type: String, default: '400px' },
})

const { center, markers, showDirections, origin, destination } = toRefs(props)

const mapContainer = ref(null)
const loading = ref(true)
const error = ref(null)

let map = null
let markerObjects = []
let directionsRenderer = null
let google = null

async function initMap() {
  try {
    const { key } = await locationService.getMapsKey()
    const loader = new Loader({
      apiKey: key,
      version: 'weekly',
      libraries: ['places'],
    })
    google = await loader.load()
    map = new google.maps.Map(mapContainer.value, {
      center: props.center,
      zoom: props.zoom,
    })
    updateMarkers()
    if (props.showDirections && props.origin && props.destination) {
      updateDirections()
    }
    loading.value = false
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
}

function clearMarkers() {
  markerObjects.forEach((m) => m.setMap(null))
  markerObjects = []
}

function updateMarkers() {
  if (!map || !google) return
  clearMarkers()
  const bounds = new google.maps.LatLngBounds()
  props.markers.forEach((m) => {
    const marker = new google.maps.Marker({
      position: { lat: m.lat, lng: m.lng },
      map,
      title: m.title || '',
    })
    if (m.label) {
      const infoWindow = new google.maps.InfoWindow({ content: m.label })
      marker.addListener('click', () => infoWindow.open(map, marker))
    }
    markerObjects.push(marker)
    bounds.extend(marker.getPosition())
  })
  if (props.markers.length > 1) {
    map.fitBounds(bounds, 60)
  }
}

function updateDirections() {
  if (!map || !google || !props.origin || !props.destination) return
  if (directionsRenderer) {
    directionsRenderer.setMap(null)
  }
  const directionsService = new google.maps.DirectionsService()
  directionsRenderer = new google.maps.DirectionsRenderer({ map, suppressMarkers: false })
  directionsService.route(
    {
      origin: props.origin,
      destination: props.destination,
      travelMode: google.maps.TravelMode.DRIVING,
    },
    (result, status) => {
      if (status === 'OK') {
        directionsRenderer.setDirections(result)
      }
    }
  )
}

onMounted(initMap)

watch(markers, updateMarkers, { deep: true })
watch([showDirections, origin, destination], () => {
  if (props.showDirections) updateDirections()
}, { deep: true })
watch(center, () => {
  if (map) map.setCenter(props.center)
}, { deep: true })
</script>

<template>
  <div class="relative rounded-lg overflow-hidden border border-gray-200">
    <div v-if="loading" class="flex items-center justify-center bg-gray-100" :style="{ height }">
      <p class="text-gray-500">Loading map...</p>
    </div>
    <div v-if="error" class="flex items-center justify-center bg-red-50" :style="{ height }">
      <p class="text-red-600 text-sm">Map error: {{ error }}</p>
    </div>
    <div ref="mapContainer" :style="{ width: '100%', height }" v-show="!loading && !error"></div>
  </div>
</template>
