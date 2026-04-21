<script setup>
/**
 * Displays the surrounding view of the application, which mainly includes the navigation side bar.
 * @module App
 */

import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

/**
 * Auth store containing user session and profile state.
 */
const auth = useAuthStore()

/**
 * Current route instance. Used for conditional navigation.
 */
const route = useRoute()

/**
 * Determines whether the user can switch between vendor and renter dashboards on the home view.
 */
const canSwitchHomeDashboards = computed(
  () => auth.isAuthenticated && auth.profileComplete && auth.user?.vendor && auth.user?.renter
)
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:left-1/2 focus:top-4 focus:z-50 focus:-translate-x-1/2 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-gray-900 focus:shadow-md"
    >
      Skip to main content
    </a>

    <header class="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <span class="text-2xl font-bold text-gray-900">SERA</span>
      <div class="flex items-center gap-3">
        <template v-if="auth.isAuthenticated">
          <span class="text-sm text-gray-700">{{ auth.user?.name }}</span>
          <router-link
            to="/logout"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Logout
          </router-link>
        </template>
        <template v-else>
          <router-link
            to="/login"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Login
          </router-link>
        </template>
      </div>
    </header>

    <!-- 100vh - header(4rem) - footer(3rem) -->
    <div class="flex h-[calc(100vh-7rem)] min-h-0">
      <aside class="w-56 bg-white border-r border-gray-200 p-4 overflow-auto">
        <nav class="space-y-2">
          <div>
            <router-link
              to="/"
              class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700"
            >
              Home
            </router-link>

            <div
              v-if="canSwitchHomeDashboards && route.name === 'home'"
              class="mt-1 ml-3 border-l border-gray-200 pl-3 space-y-1"
            >
              <span class="sr-only">Home dashboard selector</span>
              <router-link
                :to="{ name: 'home', query: { view: 'vendor' } }"
                class="block px-3 py-2 rounded-md text-sm hover:bg-gray-100 text-gray-600"
                :class="route.query.view === 'vendor' || !route.query.view ? 'bg-gray-100 text-gray-900 font-medium' : ''"
                :aria-current="route.query.view === 'vendor' || !route.query.view ? 'page' : undefined"
              >
                Vendor Dashboard
              </router-link>
              <router-link
                :to="{ name: 'home', query: { view: 'renter' } }"
                class="block px-3 py-2 rounded-md text-sm hover:bg-gray-100 text-gray-600"
                :class="route.query.view === 'renter' ? 'bg-gray-100 text-gray-900 font-medium' : ''"
                :aria-current="route.query.view === 'renter' ? 'page' : undefined"
              >
                Renter Dashboard
              </router-link>
            </div>
          </div>
          <template v-if="auth.isAuthenticated && auth.profileComplete">
            <router-link :to="{ name: 'view_profile', params: { id: auth.user?.id } }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Profile</router-link>
            <router-link v-if="auth.user?.vendor" :to="{ name: 'earnings_profile' }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Earnings</router-link>
            <router-link to="/rentals" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Rentals</router-link>
            <router-link v-if="auth.user?.vendor" to="/equipment" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Equipment</router-link>
            <router-link v-if="!auth.user?.vendor || auth.user?.renter" to="/equipment/search" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Find Equipment</router-link>
            <router-link to="/calendar" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Calendar</router-link>
          </template>
        </nav>
      </aside>

      <main id="main-content" tabindex="-1" class="flex-1 p-6 overflow-auto focus:outline-none">
        <router-view />
      </main>
    </div>

    <footer class="h-12 bg-white border-t border-gray-200 px-6 flex items-center text-sm text-gray-600">
      © 2026 SERA
    </footer>
  </div>
</template>
