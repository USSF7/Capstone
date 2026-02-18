<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-blue-600 text-white p-4">
      <nav class="container mx-auto flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold hover:text-blue-200">Capstone</router-link>
        <div class="space-x-4">
          <router-link to="/" class="hover:text-blue-400">Home</router-link>
          <router-link to="/about" class="hover:text-blue-200">About</router-link>
        </div>
      </nav>
    </header>

    <main class="flex-grow container mx-auto p-4">
      <router-view />
    </main>

    <footer class="bg-gray-200 p-4 text-center text-gray-600">
      © 2026 Capstone Project
    </footer>
  </div>
</template>