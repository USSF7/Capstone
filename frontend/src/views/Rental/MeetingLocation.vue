<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import RentalMeetingLocationField from './components/RentalMeetingLocationField.vue'

const route = useRoute()
const rentalId = computed(() => Number(route.params.id))
const location = ref('')
</script>

<template>
  <section class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Meeting Location</h1>
    <rental-meeting-location-field
      v-model="location"
      :rental-id="rentalId"
      label="Meeting Location"
    />
  </section>
</template>
