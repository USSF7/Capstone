<script setup>
import { ref, computed, watch } from 'vue'
import { FwbCard, FwbImg, FwbRating, FwbListGroup, FwbListGroupItem, FwbBadge, FwbButton } from 'flowbite-vue'

/**
 * Base URL for loading equipment images from backend
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

/**
 * Component props
 * @property {Object} rentalData - Rental object containing equipment list and metadata
 * @property {number} currentUserId - ID of the currently logged-in user
 */
const props = defineProps({
  rentalData: { type: Object, required: true },
  currentUserId: { type: Number, required: true }
})

/**
 * Component events
 * - open-review-equipment: triggers review modal
 * - send-current-equipment: sends currently selected equipment to parent
 */
const emit = defineEmits(['open-review-equipment', 'send-current-equipment'])

/**
 * Index of currently displayed equipment item
 */
const currentPage = ref(0)

/**
 * List of equipment associated with rental
 * @returns {Array} List of equipment
 */
const equipmentList = computed(() => props.rentalData?.equipment || [])

/**
 * Currently selected equipment item in carousel
 * @returns {Object|null} The current equipment
 */
const currentEquipment = computed(() => equipmentList.value[currentPage.value] || null)

/**
 * True if rental contains more than one equipment item
 */
const hasMultipleEquipment = computed(() => equipmentList.value.length > 1)

/**
 * Emits currently selected equipment whenever it changes
 */
watch(currentEquipment, (newValue) => {
  emit('send-current-equipment', newValue)
})

/**
 * True if rental is returned
 */
const isReturned = computed(() => props.rentalData.status === 'returned')

/**
 * True if current user is the vendor who owns this rental
 */
const isVendorViewer = computed(() => props.currentUserId === props.rentalData?.vendor_id)

/**
 * Determines whether current user is allowed to leave a review
 */
const canReviewEquipment = computed(() => !isVendorViewer.value)

/**
 * True if current equipment has already been reviewed
 */
const equipmentAlreadyReviewed = computed(() => {
  const equipmentReviewed = currentEquipment.value.equipment_reviewed === true
  return equipmentReviewed
})

/**
 * Ensures pagination index resets if equipment list shrinks
 */
watch(equipmentList, (newList) => {
  if (currentPage.value >= newList.length) {
    currentPage.value = 0
  }
})

/**
 * Navigates to previous equipment item
 */
function goToPreviousPage() {
  if (!hasMultipleEquipment.value) return
  currentPage.value = (currentPage.value - 1 + equipmentList.value.length) % equipmentList.value.length
}

/**
 * Navigates to next equipment item
 */
function goToNextPage() {
  if (!hasMultipleEquipment.value) return
  currentPage.value = (currentPage.value + 1) % equipmentList.value.length
}

</script>

<template>
  <fwb-card class="!max-w-full">
    <div class="p-5 space-y-4">
      <div v-if="currentEquipment" class="space-y-2">
        <fwb-img v-if="currentEquipment.picture" :alt="currentEquipment.name" img-class="rounded-lg mb-2" :src="`${BACKEND_URL}/${currentEquipment.picture}`" />
        <div v-else class="w-full h-56 mb-2 bg-gray-100 rounded-lg border border-gray-300 flex items-center justify-center">
          <span class="text-sm text-gray-400">No image available</span>
        </div>

        <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          {{ currentEquipment.name }}
        </span>

        <fwb-rating
          :rating="currentEquipment.averageRating"
          :review-link="currentEquipment ? `/equipment/${currentEquipment.id}/view` : '#'"
          :review-text="currentEquipment.numRatingsText"
        >
          <template #besideText>
            <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
              {{ currentEquipment.averageRating }} out of 5
            </p>
          </template>
        </fwb-rating>

        <fwb-badge v-if="currentEquipment.condition === 'Mint'" class="inline-block" size="sm" type="default"> {{ currentEquipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else-if="currentEquipment.condition === 'Above Average'" class="inline-block" size="sm" type="green"> {{ currentEquipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else-if="currentEquipment.condition === 'Average'" class="inline-block" size="sm" type="yellow"> {{ currentEquipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else class="inline-block" size="sm" type="red"> {{ currentEquipment.condition }} Condition </fwb-badge>

        <fwb-list-group class="w-auto">
          <fwb-list-group-item class="!flex !flex-col !items-start">
            <b class="mr-1">Description:</b>
            <span>{{ currentEquipment.description || 'No description provided.' }}</span>
          </fwb-list-group-item>
        </fwb-list-group>

        <div v-if="isReturned" class="flex mt-4">
          <fwb-button
            v-if="(canReviewEquipment === true) && (equipmentAlreadyReviewed === false)"
            color="default"
            class="flex-1"
            @click="$emit('open-review-equipment')"
          >
            Review Equipment
          </fwb-button>
          <fwb-button
            v-else-if="canReviewEquipment"
            color="default"
            class="flex-1"
            @click="$emit('open-review-equipment')"
            disabled
          >
            Review Equipment
          </fwb-button>
        </div>

      </div>

      <div v-if="currentEquipment && hasMultipleEquipment" class="flex items-center justify-center gap-3 pt-2">
        <button
          type="button"
          class="h-8 w-8 rounded-full border border-gray-300 text-gray-700 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          aria-label="Previous equipment"
          @click="goToPreviousPage"
        >
          &#8592;
        </button>

        <button
          v-for="(item, idx) in equipmentList"
          :key="item.id"
          type="button"
          class="h-4 w-4 rounded-full transition-colors"
          :class="idx === currentPage ? 'bg-blue-600' : 'bg-gray-300 hover:bg-gray-400'"
          :aria-label="`Go to equipment ${idx + 1}`"
          @click="currentPage = idx"
        />

        <button
          type="button"
          class="h-8 w-8 rounded-full border border-gray-300 text-gray-700 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          aria-label="Next equipment"
          @click="goToNextPage"
        >
          &#8594;
        </button>
      </div>
    </div>
  </fwb-card>
</template>

<style scoped>
</style>