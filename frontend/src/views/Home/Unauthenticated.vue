<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { FwbButton } from 'flowbite-vue'

const auth = useAuthStore()
const router = useRouter()
</script>

<template>
  <section class="max-w-3xl mx-auto text-center">
    <div class="py-16">
      <h1 class="text-4xl font-bold text-gray-800 mb-4">Welcome to SERA</h1>
      <p class="text-lg text-gray-500 mb-8">Share, rent, and discover equipment in your neighborhood.</p>
      <div v-if="!auth.isAuthenticated" class="flex justify-center gap-4">
        <fwb-button @click="router.push({ name: 'login' })">Get Started</fwb-button>
      </div>
    </div>
  </section>
</template>
