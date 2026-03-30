<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <header class="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">SERA</h1>
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
          <router-link to="/" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Home</router-link>
          <router-link to="/about" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">About</router-link>
          <router-link to="/users" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Users</router-link>
          <template v-if="auth.isAuthenticated && auth.profileComplete">
            <router-link :to="{ name: 'view_profile', params: { id: auth.user?.id } }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Profile</router-link>
            <router-link :to="{ name: 'earnings_profile' }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Earnings</router-link>
            <router-link to="/inventory" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Inventory</router-link>
            <router-link to="/requests" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Requests</router-link>
            <router-link to="/rentals" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Rentals</router-link>
            <router-link to="/events" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Events</router-link>
            <router-link to="/recommendations" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Recommendations</router-link>
            <router-link to="/equipment" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Equipment</router-link>
            <router-link to="/calendar" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Calendar</router-link>
          </template>
        </nav>
      </aside>

      <main class="flex-1 p-6 overflow-auto">
        <router-view />
      </main>
    </div>

    <footer class="h-12 bg-white border-t border-gray-200 px-6 flex items-center text-sm text-gray-600">
      © 2026 SERA
    </footer>
  </div>
</template>
