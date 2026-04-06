<script setup>
import { ref, computed } from 'vue'
import { FwbCard, FwbImg, FwbRating, FwbListGroup, FwbListGroupItem, FwbBadge } from 'flowbite-vue'
import { useScroll } from '@vueuse/core'

const props = defineProps({
  rentalData: { type: Object, required: true },
  currentUserId: { type: Number, required: true }
})

const el = ref(null)
const y = useScroll(el)

</script>

<template>
  <fwb-card class="!max-w-full">
    <div ref="el" class="scroll-container p-5 space-y-2">
      <div v-for="equipment in props.rentalData.equipment" :key="equipment.id" class="space-y-2">
        <fwb-img alt="flowbite-vue" img-class="rounded-lg" src="../../../image.jpg" />

        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          {{ equipment.name }}
        </h5>

        <fwb-rating
          :rating="equipment.averageRating"
          :review-link="equipment ? `/equipment/${equipment.id}/view` : '#'"
          :review-text="equipment.numRatingsText"
        >
          <template #besideText>
            <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
              {{ equipment.averageRating }} out of 5
            </p>
          </template>
        </fwb-rating>

        <fwb-badge v-if="equipment.condition === 'Mint'" class="inline-block" size="sm" type="default"> {{ equipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else-if="equipment.condition === 'Above Average'" class="inline-block" size="sm" type="green"> {{ equipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else-if="equipment.condition === 'Average'" class="inline-block" size="sm" type="yellow"> {{ equipment.condition }} Condition </fwb-badge>
        <fwb-badge v-else class="inline-block" size="sm" type="red"> {{ equipment.condition }} Condition </fwb-badge>

        <fwb-list-group class="w-auto">
          <fwb-list-group-item class="!flex !flex-col !items-start">
            <b class="mr-1">Description:</b>
            <span>{{ equipment.description || 'No description provided.' }}</span>
          </fwb-list-group-item>
        </fwb-list-group>
        <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
      </div>
    </div>
  </fwb-card>
</template>

<style scoped>

.scroll-container {
  overflow-y: auto;
  height: 596px;
}

</style>