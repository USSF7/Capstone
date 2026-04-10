<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import VendorView from './Vendor.vue'
import RenterView from './Renter.vue'
import UnauthenticatedView from './Unauthenticated.vue'

const auth = useAuthStore()
const route = useRoute()

const isRenter = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.renter)
const isVendor = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.vendor)

const displayedView = computed(() => {
  if (!auth.isAuthenticated || !auth.profileComplete) return 'unauthenticated'
  if (route.query.view === 'vendor' && isVendor.value) return 'vendor'
  if (route.query.view === 'renter' && isRenter.value) return 'renter'
  if (isVendor.value) return 'vendor'
  if (isRenter.value) return 'renter'
  return 'unauthenticated'
})
</script>

<template>
  <vendor-view v-if="displayedView === 'vendor'" />
  <renter-view v-else-if="displayedView === 'renter'" />
  <unauthenticated-view v-else />
</template>
