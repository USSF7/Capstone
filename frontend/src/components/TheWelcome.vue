<script setup>
import WelcomeItem from './WelcomeItem.vue'
</script>

<template>
  <div class="grid md:grid-cols-3 gap-6">
    <WelcomeItem>
      <template #heading>Welcome</template>
      <em class="text-blue-900">Howdy</em>
    </WelcomeItem>

    <WelcomeItem>
      <template #heading>Vue Ecosystem</template>
      <p class="text-gray-900">
        Get inspired by the
        <a target="_blank" href="https://github.com/vuejs/awesome-vue" class="text-blue-600 hover:underline">awesome Vue</a>
        ecosystem.
      </p>
    </WelcomeItem>

    <WelcomeItem>
      <template #heading>Support Vue</template>
      <p class="text-gray-700">
        Vue is an MIT-licensed open source project. You can support its development via
        <a target="_blank" href="https://github.com/sponsors/yyx990803" class="text-blue-600 hover:underline">sponsoring</a>.
      </p>
    </WelcomeItem>
  </div>
</template>