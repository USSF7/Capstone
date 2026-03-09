<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <header class="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">SERA</h1>
      <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
        Login
      </button>
    </header>

    <!-- 100vh - header(4rem) - footer(3rem) -->
    <div class="flex h-[calc(100vh-7rem)] min-h-0">
      <aside class="w-56 bg-white border-r border-gray-200 p-4 overflow-auto">
        <nav class="space-y-2">
          <router-link to="/" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Home</router-link>
          <router-link to="/about" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">About</router-link>
          <router-link to="/users" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Users</router-link>
          <router-link :to="{ name: 'create_profile' }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">Register</router-link>
          <router-link :to="{ name: 'view_profile' }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Profile</router-link>
          <router-link :to="{ name: 'earnings_profile' }" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Earnings</router-link>
          <router-link to="/requests" class="block px-3 py-2 rounded-md hover:bg-gray-100 text-gray-700">My Requests</router-link>
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