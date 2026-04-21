<!-- Page for a user to manage their own inventory (My inventory) -->

<script lang="js" setup>

    /**
     * The index page for the inventory view
     * @module InventoryIndex
     */

    import { onMounted, ref, computed } from 'vue'
    import { FwbCard, FwbButton, FwbBadge, FwbRating } from 'flowbite-vue'
    import { useAuthStore } from '../../stores/auth'
    import EquipmentService from '../../services/equipmentService'
    import UserService from '../../services/userService'

    /**
     * Base URL for backend assets (used for image rendering).
     */
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

    /**
     * Auth store containing user identity and session data.
     */
    const auth = useAuthStore()

    /**
     * Full user object returned from backend, which includes inventory.
     */
    const userData = ref()

    /**
     * User interface state for fetching user and inventory data.
     */
    const loading = ref(true)

    /**
     * Holds any API or runtime error messages for display.
     */
    const error = ref('')

    /**
     * Computed current authenticated user ID.
     */
    const userId = computed(() => auth.user?.id)

    /**
     * Derived inventory list from loaded user data.
     * Falls back to empty array if not yet loaded.
     */
    const inventory = computed(() => userData.value?.inventory || [])

    /**
     * Converts equipment condition into user interface badge color type.
     * 
     * @param {string} condition - The condition of the equipment.
     * @returns {string} The badge color symbolizing the condition of the equipment.
     */
    function getConditionBadgeType(condition) {
      if (condition === 'Mint') return 'default'
      if (condition === 'Above Average') return 'green'
      if (condition === 'Average') return 'yellow'
      return 'red'
    }

    /**
     * Loads the full user profile, which is used as a base data container.
     */
    async function loadUser() {
        // Get the current user's data
        userData.value = await UserService.getUser(userId.value)
    }

    /**
     * Loads equipment owned by the current user.
     * Overwrites userData.inventory after user is loaded.
     */
    async function loadInventory() {
        // Get the current user's inventory data
        userData.value.inventory = await EquipmentService.getEquipmentByOwner(userId.value)
    }

    /**
     * Deletes an equipment item after confirmation.
     */
    async function deleteEquipment(equipmentId) {
        if (!confirm('Are you sure you want to delete this equipment?')) return
        try {
            await EquipmentService.deleteEquipment(equipmentId)
            await loadInventory()
        } catch (err) {
            error.value = err.message || 'Failed to delete equipment'
            console.error('Error deleting equipment:', err)
        }
    }

    /**
     * Loading user data and their equipment inventory data.
     */
    onMounted(async () => {
        await loadUser()
        await loadInventory()
        loading.value = false
    })
</script>

<template>
  <section>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Inventory</h1>
      <router-link
        to="/equipment/create"
        class="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
      >
        Add Equipment
      </router-link>
    </div>

    <p v-if="loading" class="text-gray-600">Loading inventory...</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <p v-else-if="inventory.length === 0" class="text-gray-600">You have not added any equipment yet.</p>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <fwb-card
        v-for="equipment in inventory"
        :key="equipment.id"
        class="overflow-hidden"
      >
        <div class="p-4 space-y-4">
          <div class="rounded-xl border border-2 border-gray-800">
            <div v-if="equipment.picture">
              <img :src="`${BACKEND_URL}/${equipment.picture}`" :alt="equipment.name" class="w-full h-48 object-cover rounded-lg" />
            </div>
            <div v-else class="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center">
              <span class="text-sm text-gray-400">No image available</span>
            </div>
          </div>

          <div class="space-y-3">
            <span class="text-xl font-bold tracking-tight text-gray-900 dark:text-white block">
              {{ equipment.name }}
            </span>

            <div class="flex items-center justify-between gap-2">
              <fwb-badge :type="getConditionBadgeType(equipment.condition)" size="sm">
                {{ equipment.condition || 'Condition not set' }}
              </fwb-badge>
              <span class="text-lg font-semibold text-blue-600">${{ equipment.price }}/day</span>
            </div>

            <fwb-rating
              size="sm"
              :rating="equipment.average_rating || 0"
              :review-text="`${equipment.rating_count || 0} review${(equipment.rating_count || 0) === 1 ? '' : 's'}`"
            >
              <template #besideText>
                <span class="ml-2 text-sm text-gray-600">
                  {{ equipment.average_rating ? `${equipment.average_rating} / 5` : 'No ratings yet' }}
                </span>
              </template>
            </fwb-rating>

            <p class="text-sm text-gray-600 line-clamp-2">
              {{ equipment.description || 'No description provided.' }}
            </p>

            <div class="pt-3 mt-1 border-t border-gray-200 flex flex-wrap gap-2">
              <router-link :to="{ name: 'equipment-view', params: { id: equipment.id } }" class="flex-1 min-w-[90px]">
                <fwb-button color="light" class="w-full">View</fwb-button>
              </router-link>
              <router-link :to="{ name: 'equipment-edit', params: { id: equipment.id } }" class="flex-1 min-w-[90px]">
                <fwb-button color="yellow" class="w-full">Edit</fwb-button>
              </router-link>
              <fwb-button color="red" class="flex-1 min-w-[90px]" @click="deleteEquipment(equipment.id)">Delete</fwb-button>
            </div>
          </div>
        </div>
      </fwb-card>
    </div>
  </section>
</template>
