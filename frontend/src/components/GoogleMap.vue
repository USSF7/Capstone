<script setup>
/**
 * Google Maps functions
 * @module GoogleMaps
 */

import { ref, onMounted, watch, toRefs } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'
import locationService from '../services/locationService'

/**
 * Latitude/longitude coordinate.
 * @typedef {{ lat: number, lng: number }} LatLng
 */

/**
 * Marker displayed on the map.
 * @typedef {Object} MapMarker
 * @property {number} lat - Latitude coordinate value
 * @property {number} lng - Longitude coordinate value
 * @property {string} [title] - Title of the marker
 * @property {string} [label] - Info window content
 * @property {string} [color] - Custom marker color
 * @property {boolean} [selected] - Highlights marker
 * @property {number} [zIndex] - The index of the marker
 */

/**
 * Component props.
 * @typedef {Object} Props
 * @property {LatLng} center - Initial map center
 * @property {number} [zoom=13] - Initial zoom level
 * @property {MapMarker[]} [markers=[]] - Markers to render
 * @property {boolean} [showDirections=false] - Whether to display route
 * @property {LatLng|null} [origin=null] - Route origin
 * @property {LatLng|null} [destination=null] - Route destination
 * @property {string} [height='400px'] - Map container height
 */

/** @type {Props} */
const props = defineProps({
  center: { type: Object, required: true },
  zoom: { type: Number, default: 13 },
  markers: { type: Array, default: () => [] },
  showDirections: { type: Boolean, default: false },
  origin: { type: Object, default: null },
  destination: { type: Object, default: null },
  height: { type: String, default: '400px' },
})

/**
 * Emits map-related events.
 * @type {(event: 'marker-click', marker: MapMarker) => void}
 */
const emit = defineEmits(['marker-click'])

const { center, markers, showDirections, origin, destination } = toRefs(props)

/**
 * DOM element for mounting the Google Map.
 * @type {import('vue').Ref<HTMLElement|null>}
 */
const mapContainer = ref(null)

/**
 * Loading state for map initialization.
 * @type {import('vue').Ref<boolean>}
 */
const loading = ref(true)

/**
 * Error message if map fails to load.
 * @type {import('vue').Ref<string|null>}
 */
const error = ref(null)

/**
 * Holds the google maps object.
 * @type {google.maps.Map|null}
 */
let map = null

/**
 * Holds all of the marker objects in the map.
 * @type {google.maps.Marker[]}
 */
let markerObjects = []

/**
 * Holds the direction render information.
 * @type {google.maps.DirectionsRenderer|null}
 */
let directionsRenderer = null

/**
 * Holds the data to Google.
 * @type {typeof google|null}
 */
let google = null

/**
 * Window that displays Google Maps information.
 * @type {google.maps.InfoWindow|null}
 */
let activeInfoWindow = null

/**
 * Initializes the Google Map and loads markers and directions.
 */
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

/**
 * Removes all markers and closes any open info window.
 */
function clearMarkers() {
  markerObjects.forEach((m) => m.setMap(null))
  markerObjects = []
  if (activeInfoWindow) {
    activeInfoWindow.close()
    activeInfoWindow = null
  }
}

/**
 * Renders markers on the map based on props.
 */
function updateMarkers() {
  if (!map || !google) return
  clearMarkers()
  const bounds = new google.maps.LatLngBounds()
  props.markers.forEach((m) => {
    const markerOptions = {
      position: { lat: m.lat, lng: m.lng },
      map,
      title: m.title || '',
      zIndex: m.zIndex,
    }

    if (m.color || m.selected) {
      markerOptions.icon = {
        path: google.maps.SymbolPath.CIRCLE,
        scale: m.selected ? 9 : 7,
        fillColor: m.color || '#2563EB',
        fillOpacity: 1,
        strokeColor: '#FFFFFF',
        strokeWeight: 1.5,
      }
    }

    const marker = new google.maps.Marker({
      ...markerOptions,
    })

    marker.addListener('click', () => {
      emit('marker-click', m)
    })

    if (m.label) {
      const infoWindow = new google.maps.InfoWindow({ content: m.label })
      marker.addListener('click', () => {
        if (activeInfoWindow && activeInfoWindow !== infoWindow) {
          activeInfoWindow.close()
        }
        infoWindow.open(map, marker)
        activeInfoWindow = infoWindow
      })
    }
    markerObjects.push(marker)
    bounds.extend(marker.getPosition())
  })
  if (props.markers.length > 1) {
    map.fitBounds(bounds, 60)
  }
}

/**
 * Fetches and renders driving directions between origin and destination.
 */
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

/**
 * Lifecycle of the component.
 */
onMounted(initMap)

/**
 * Updates markers when marker data changes
 */
watch(markers, updateMarkers, { deep: true })

/**
 * Updates directions when routing-related props change
 */
watch([showDirections, origin, destination], () => {
  if (props.showDirections) updateDirections()
}, { deep: true })

/**
 * Re-centers map when center changes
 */
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

<style scoped>
:deep(.gm-ui-hover-effect) {
  display: none !important;
}
</style>
