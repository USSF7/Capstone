<!-- Page for a user to manage their own inventory (My inventory) -->

<script lang="js" setup>

    import { onMounted, ref, computed } from 'vue'
    import { FwbCard, FwbButton } from 'flowbite-vue'
    import { useAuthStore } from '../../stores/auth'
    import EquipmentService from '../../services/equipmentService'
    import UserService from '../../services/userService'

    const auth = useAuthStore()
    const userData = ref()
    const loading = ref(true)
    const error = ref('')
    const userId = computed(() => auth.user?.id)

    async function loadUser() {
        // Get the current user's data
        userData.value = await UserService.getUser(userId.value)
    }

    async function loadInventory() {
        // Get the current user's inventory data
        userData.value.inventory = await EquipmentService.getEquipmentByOwner(userId.value)
    }

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

    <div v-else class="grid grid-cols-3 gap-4">
      <fwb-card
        v-for="equipment in userData.inventory"
        :key="equipment.id"
        class="w-sm relative"
      >
        <div class="top-2 right-2 flex gap-2">
          <router-link :to="{ name: 'equipment-edit', params: { id: equipment.id } }">
            <fwb-button color="Yellow" pill>Edit</fwb-button>
          </router-link>
          <router-link :to="{ name: 'equipment-view', params: { id: equipment.id }}">
            <fwb-button color="black" pill>View</fwb-button>
          </router-link>
          <fwb-button color="Red" pill @click="deleteEquipment(equipment.id)">Delete</fwb-button>
        </div>

        <div class="p-5">
          <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            Equipment name: {{ equipment.name }}
          </h5>
          <ul>
            <li><strong>Status:</strong> {{ equipment.status }}</li>
            <li v-if="equipment.transaction_id"><strong>Current Transaction ID:</strong> {{ equipment.transaction_id }}</li>
          </ul>
        </div>
      </fwb-card>
    </div>
  </section>
</template>
