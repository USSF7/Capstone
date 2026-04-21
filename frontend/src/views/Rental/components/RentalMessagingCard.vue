<script setup>
import { FwbCard } from 'flowbite-vue'
import MessageBox from '../../../components/Messaging/MessageBox.vue'

/**
 * Component props
 * @property {number} currentUserId - ID of logged-in user
 * @property {number} otherUserId - ID of conversation partner
 * @property {number} rentalId - Rental context ID for scoped messaging
 */
defineProps({
  currentUserId: { type: Number, required: true },
  otherUserId: { type: Number, required: true },
  rentalId: { type: Number, required: true },
})
</script>

<template>
  <fwb-card class="!max-w-full">
    <div class="p-5 space-y-3">
      <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Messaging</span>
      <message-box
        :current-user-id="currentUserId"
        :other-user-id="otherUserId"
        :rental-id="rentalId"
        title="Conversation"
      />
    </div>
  </fwb-card>
</template>
