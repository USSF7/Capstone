<script setup>
import TheWelcome from '../components/TheWelcome.vue'

import { ref } from 'vue'
import { FwbTextarea, FwbAlert } from 'flowbite-vue'

const message = ref('')
</script>

<template>
  <div class="text-center">
    <h1 class="text-4xl font-bold text-gray-800 mb-8">Welcome to Capstone</h1>
    <TheWelcome />

    <fwb-textarea
      v-model="message"
      :rows="4"
      label="Your message"
      placeholder="Write your message..."
    />
  </div>
</template>