<script setup>
import { FwbCard, FwbProgress } from 'flowbite-vue'

/**
 * Month names used for human-readable date formatting.
 * @type {string[]}
 */
const months = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
]

/**
 * Component props
 * @property {Object} rental - Rental object containing equipment, pricing, and dates
 * @property {string} priceLabel - Label used for pricing display
 * @property {number} progress - Progress percentage (0–100) for rental status
 * @property {string} progressLabel - Label describing current rental status
 * @property {string} [progressColor] - Optional color override for progress bar
 */
const props = defineProps({
  rental: {
    type: Object,
    required: true,
  },
  priceLabel: {
    type: String,
    default: 'Price',
  },
  progress: {
    type: Number,
    required: true,
  },
  progressLabel: {
    type: String,
    required: true,
  },
  progressColor: {
    type: String,
    default: undefined,
  },
})

/**
 * Emits:
 * - select: triggered when the rental card is clicked
 */
const emit = defineEmits(['select'])

/**
 * Backend base URL for serving uploaded equipment images.
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

/**
 * Formats an ISO date string into a human-readable format.
 *
 * @param {string} isoDate The date in ISO format
 * @returns {string} Human-readable formatted date
 */
function dateFormatting(isoDate) {
  const date = new Date(isoDate)
  const day = date.getDate()
  const month = date.getMonth()
  const year = date.getFullYear()
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')

  return months[month] + ' ' + day.toString() + ', ' + year.toString() + ' ' + hour + ':' + minute
}

/**
 * Returns the first equipment item in a rental.
 *
 * @param {Object} rental The rental object, whichs stores the rental's information.
 * @returns {Object|null} The first rental object.
 */
function getFirstEquipment(rental) {
  if (!Array.isArray(rental?.equipment) || rental.equipment.length === 0) return null
  return rental.equipment[0]
}

/**
 * Returns the preview image path for a rental.
 *
 * @param {Object} rental The rental object, whichs stores the rental's information.
 * @returns {string|null} The image URL
 */
function getRentalPreviewImage(rental) {
  return getFirstEquipment(rental)?.picture || null
}

/**
 * Returns alt text for the rental preview image.
 *
 * @param {Object} rental The rental object, whichs stores the rental's information.
 * @returns {string} The alt text for the rental preview image.
 */
function getRentalPreviewAlt(rental) {
  const firstEquipment = getFirstEquipment(rental)
  if (firstEquipment?.name) return `${firstEquipment.name} image`
  return 'Equipment image'
}

/**
 * Builds a display title for the rental based on equipment names.
 *
 * @param {Object} rental The rental object, whichs stores the rental's information.
 * @returns {string} The display title for the rental
 */
function getRentalTitle(rental) {
  return rental.equipment?.length ? rental.equipment.map((e) => e.name).join(', ') : 'Equipment request'
}
</script>

<template>
  <fwb-card class="!max-w-full cursor-pointer hover:shadow-lg transition-shadow" @click="emit('select')">
    <div class="flex flex-col p-5 gap-4">
      <div class="flex gap-4">
        <img
          v-if="getRentalPreviewImage(props.rental)"
          :src="`${BACKEND_URL}/${getRentalPreviewImage(props.rental)}`"
          :alt="getRentalPreviewAlt(props.rental)"
          class="w-48 h-32 object-cover rounded-lg border-2 border-gray-800"
        />
        <div v-else class="w-48 h-32 rounded-lg bg-gray-100 flex items-center justify-center text-sm text-gray-500">
          No image
        </div>
        <div class="flex flex-col space-y-2">
          <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ getRentalTitle(props.rental) }}</span>
          <p class="font-normal text-gray-700 dark:text-gray-400"><b>{{ props.priceLabel }}:</b> ${{ props.rental.agreed_price }}</p>
          <p class="font-normal text-gray-700 dark:text-gray-400"><b>Dates:</b> {{ dateFormatting(props.rental.start_date) }} through {{ dateFormatting(props.rental.end_date) }}</p>
        </div>
      </div>
      <fwb-progress class="font-normal text-gray-700 dark:text-gray-400" :progress="props.progress" size="md" :color="props.progressColor" :label="props.progressLabel" />
    </div>
  </fwb-card>
</template>
