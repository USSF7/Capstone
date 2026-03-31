<script setup>
import { computed } from 'vue'
import { FwbCard, FwbImg, FwbRating, FwbListGroup, FwbListGroupItem } from 'flowbite-vue'

const props = defineProps({
  rentalData: { type: Object, required: true },
  vendorData: { type: Object, required: true },
  renterData: { type: Object, required: true },
  currentUserId: { type: Number, required: true },
  averageRating: { type: Number, required: true },
  numRatingsText: { type: String, required: true },
})

const primaryEquipment = computed(() => props.rentalData?.equipment?.[0] || null)
const equipmentNames = computed(() =>
  (props.rentalData?.equipment || []).map((item) => item.name).join(', ')
)
const isVendorViewer = computed(() => props.currentUserId === props.rentalData?.vendor_id)
const counterpartyLabel = computed(() => (isVendorViewer.value ? 'Renter' : 'Vendor'))
const counterpartyData = computed(() => (isVendorViewer.value ? props.renterData : props.vendorData))
</script>

<template>
  <fwb-card class="!max-w-full">
    <div class="p-5 space-y-2">
      <fwb-img alt="flowbite-vue" img-class="rounded-lg" src="../../../image.jpg" />

      <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
        {{ equipmentNames || 'Equipment Request' }}
      </h5>

      <fwb-rating
        :rating="averageRating"
        :review-link="primaryEquipment ? `/equipment/${primaryEquipment.id}/view` : '#'
        "
        :review-text="numRatingsText"
      >
        <template #besideText>
          <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
            {{ averageRating }} out of 5
          </p>
        </template>
      </fwb-rating>

      <fwb-list-group class="w-auto">
        <fwb-list-group-item>
          <b class="mr-1">Price:</b> ${{ rentalData.agreed_price }}
        </fwb-list-group-item>
        <fwb-list-group-item>
          <b class="mr-1">{{ counterpartyLabel }}:</b>
          <router-link
            :to="{ name: 'view_profile', params: { id: counterpartyData.id } }"
            class="text-blue-600 hover:underline"
          >
            {{ counterpartyData.name }}
          </router-link>
        </fwb-list-group-item>
        <fwb-list-group-item class="!flex !flex-col !items-start">
          <b class="mr-1">Description:</b>
          <span>{{ primaryEquipment?.description || 'No description provided.' }}</span>
        </fwb-list-group-item>
      </fwb-list-group>
    </div>
  </fwb-card>
</template>
