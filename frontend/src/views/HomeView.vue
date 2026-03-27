<script setup>
import TheWelcome from '../components/TheWelcome.vue'

import { computed, onMounted, ref, watch } from 'vue'
import { FwbButton, FwbTextarea } from 'flowbite-vue'
import AIService from '../services/aiService'
import EquipmentService from '../services/equipmentService'
import UserService from '../services/userService'

const selectedModelType = ref('equipment')
const selectedModelId = ref('')
const optionsLoading = ref(false)
const equipmentOptions = ref([])
const userOptions = ref([])
const summaryLoading = ref(false)
const summaryError = ref('')
const summaryText = ref('')

const modelOptions = computed(() =>
  selectedModelType.value === 'equipment' ? equipmentOptions.value : userOptions.value
)

async function loadOptionsForType(modelType) {
  optionsLoading.value = true
  try {
    if (modelType === 'equipment') {
      if (equipmentOptions.value.length === 0) {
        equipmentOptions.value = await EquipmentService.getEquipment()
      }
    } else if (userOptions.value.length === 0) {
      userOptions.value = await UserService.getUsers()
    }

    selectedModelId.value = modelOptions.value.length ? String(modelOptions.value[0].id) : ''
  } catch (e) {
    summaryError.value = e.message || 'Failed to load model options.'
    selectedModelId.value = ''
  } finally {
    optionsLoading.value = false
  }
}

async function summarizeReviews() {
  summaryError.value = ''
  summaryText.value = ''

  const modelId = Number(selectedModelId.value)
  if (!selectedModelId.value || Number.isNaN(modelId) || modelId <= 0) {
    summaryError.value = 'Please choose a valid model.'
    return
  }

  summaryLoading.value = true
  try {
    const result = await AIService.summarizeReviews(selectedModelType.value, modelId)
    summaryText.value = result.summary || 'No summary returned.'
  } catch (e) {
    summaryError.value = e.message || 'Failed to summarize reviews.'
  } finally {
    summaryLoading.value = false
  }
}

watch(selectedModelType, async (newType) => {
  summaryError.value = ''
  summaryText.value = ''
  await loadOptionsForType(newType)
})

onMounted(async () => {
  await loadOptionsForType(selectedModelType.value)
})
</script>

<template>
  <section class="max-w-3xl mx-auto">
    <h1 class="text-4xl font-bold text-gray-800 mb-8">Welcome to Capstone</h1>
    <TheWelcome />

    <div class="bg-white rounded-lg shadow p-6 mt-8 text-left">
      <h2 class="text-xl font-semibold mb-4">AI Review Summary</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Model Type</label>
          <select
            v-model="selectedModelType"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="equipment">equipment</option>
            <option value="user">user</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ selectedModelType === 'equipment' ? 'Equipment Name' : 'User Name' }}
          </label>
          <select
            v-model="selectedModelId"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            :disabled="optionsLoading"
          >
            <option value="" disabled>
              {{ optionsLoading ? 'Loading options...' : 'Select an option' }}
            </option>
            <option
              v-for="item in modelOptions"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.name }} (ID: {{ item.id }})
            </option>
          </select>
        </div>

        <div>
          <fwb-button color="Blue" :disabled="summaryLoading || optionsLoading || !selectedModelId" @click="summarizeReviews">
            {{ summaryLoading ? 'Summarizing...' : 'Summarize Reviews' }}
          </fwb-button>
        </div>
      </div>

      <p v-if="summaryError" class="text-red-600 mt-3">{{ summaryError }}</p>

      <fwb-textarea
        class="mt-4"
        :rows="6"
        label="Summary"
        placeholder="AI summary will appear here..."
        :model-value="summaryText"
        readonly
      />
    </div>
  </section>
</template>