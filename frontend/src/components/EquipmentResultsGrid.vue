<script setup>
import { FwbCard, FwbBadge } from 'flowbite-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

defineProps({
  items: {
    type: Array,
    required: true,
  },
})

function getLink(item) {
  return { name: 'equipment-view', params: { id: item.id } }
}

function goToVendorProfile(ownerId) {
  if (!ownerId) return
  router.push({ name: 'view_profile', params: { id: ownerId } })
}
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <router-link
      v-for="item in items"
      :key="item.id"
      :to="getLink(item)"
      class="block rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
    >
      <fwb-card class="cursor-pointer hover:shadow-lg transition-shadow">
        <div class="p-4">
          <div v-if="item.picture" class="mb-3">
            <img :src="item.picture" :alt="item.name" class="w-full h-48 object-cover rounded-lg" />
          </div>
          <div v-else class="mb-3 w-full h-32 bg-gray-100 rounded-lg flex items-center justify-center">
            <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900 truncate">{{ item.name }}</h3>
          <fwb-badge v-if="item.condition === 'Mint'" class="inline-block mt-1 mb-1" size="sm" type="default"> {{ item.condition }} Condition </fwb-badge>
          <fwb-badge v-else-if="item.condition === 'Above Average'" class="inline-block mt-1 mb-1" size="sm" type="green"> {{ item.condition }} Condition </fwb-badge>
          <fwb-badge v-else-if="item.condition === 'Average'" class="inline-block mt-1 mb-1" size="sm" type="yellow"> {{ item.condition }} Condition </fwb-badge>
          <fwb-badge v-else class="inline-block mt-1 mb-1" size="sm" type="red"> {{ item.condition }} Condition </fwb-badge>

          <p v-if="item.description" class="text-sm text-gray-500 mt-1 line-clamp-2">{{ item.description }}</p>

          <p class="text-sm text-gray-700 mt-2">
            <span class="font-medium">Vendor:</span>
            <button
              v-if="item.owner_id"
              type="button"
              class="text-blue-600 hover:underline"
              @click.stop.prevent="goToVendorProfile(item.owner_id)"
            >
              {{ item.owner_name || 'Unknown vendor' }}
            </button>
            <span v-else>{{ item.owner_name || 'Unknown vendor' }}</span>
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
          <p class="text-xs text-gray-500 mt-1">{{ item.owner_city }}, {{ item.owner_state }}</p>
        </div>
      </fwb-card>
    </router-link>
  </div>
</template>
