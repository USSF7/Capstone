<script setup>
/**
 * Home page index view
 * @module HomeIndex
 */

import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import VendorView from './Vendor.vue'
import RenterView from './Renter.vue'
import UnauthenticatedView from './Unauthenticated.vue'

/**
 * Auth store containing user session and role information.
 */
const auth = useAuthStore()

/**
 * Current route used to read query parameters.
 */
const route = useRoute()

/**
 * Whether the user can access renter functionality.
 */
const isRenter = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.renter)

/**
 * Whether the user can access vendor functionality.
 */
const isVendor = computed(() => auth.isAuthenticated && auth.profileComplete && auth.user?.vendor)

/**
 * Determines which view should be displayed.
 *
 * @returns {'vendor' | 'renter' | 'unauthenticated'} The type of view to display.
 */
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
