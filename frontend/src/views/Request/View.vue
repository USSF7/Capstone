<!-- View a specific request details and message with potential vendors and messages placeholder -->
<template>
  <section>
    <div class="grid grid-cols-2 gap-4">
      <!-- Left: Request details -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-2xl font-semibold mb-4">Request Details</h2>
        <div v-if="loading" class="text-gray-600">Loading...</div>
        <div v-else-if="error" class="text-red-600">{{ error }}</div>
        <div v-else>
          <p><strong>Equipment:</strong> {{ request.name }}</p>
          <p><strong>Event:</strong> {{ request.event_name || '—' }}</p>
          <p><strong>Max Price:</strong> {{ request.max_price }}</p>
          <p><strong>Count:</strong> {{ request.count }}</p>
          <p><strong>Start:</strong> {{ formatDate(request.start_date) }}</p>
          <p><strong>End:</strong> {{ formatDate(request.end_date) }}</p>
          <p><strong>Location:</strong> {{ request.location }}</p>
          <p><strong>Comments:</strong> {{ request.comments }}</p>
          <p><strong>Status:</strong> {{ request.status }}</p>
        </div>
      </div>

      <!-- Right: Potential Vendors (top) and Messages (bottom) -->
      <div class="flex flex-col gap-4">
        <div class="bg-white rounded-lg shadow p-4 flex-1 overflow-auto">
          <h3 class="text-lg font-medium mb-3">Potential Vendors</h3>
          <fwb-table>
            <fwb-table-head>
              <fwb-table-head-cell>Vendor</fwb-table-head-cell>
              <fwb-table-head-cell>Rating</fwb-table-head-cell>
              <fwb-table-head-cell>Price</fwb-table-head-cell>
              <fwb-table-head-cell>
                <span class="sr-only">Contact</span>
              </fwb-table-head-cell>
            </fwb-table-head>
            <fwb-table-body>
              <fwb-table-row>
                <fwb-table-cell>Acme Rentals</fwb-table-cell>
                <fwb-table-cell>4.5</fwb-table-cell>
                <fwb-table-cell>$120</fwb-table-cell>
                <fwb-table-cell>
                  <fwb-a href="#">Contact</fwb-a>
                </fwb-table-cell>
              </fwb-table-row>
              <fwb-table-row>
                <fwb-table-cell>Pro Sound Co.</fwb-table-cell>
                <fwb-table-cell>4.2</fwb-table-cell>
                <fwb-table-cell>$150</fwb-table-cell>
                <fwb-table-cell>
                  <fwb-a href="#">Contact</fwb-a>
                </fwb-table-cell>
              </fwb-table-row>
            </fwb-table-body>
          </fwb-table>
        </div>

        <div class="bg-white rounded-lg shadow p-4 h-48">
          <h3 class="text-lg font-medium mb-3">Messages</h3>
          <div class="border border-dashed border-gray-300 h-full rounded p-4 text-gray-500">Messages placeholder</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  FwbA,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from 'flowbite-vue'
import requestService from '../../services/requestService'
import eventService from '../../services/eventService'

const route = useRoute()
const request = ref({})
const loading = ref(true)
const error = ref('')

function formatDate(iso) {
  if (!iso) return '—'
  return iso.split('T')[0]
}

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'No request id provided'
    loading.value = false
    return
  }

  try {
    const req = await requestService.getRequest(id)
    request.value = req
    // ensure event name is present
    if (!request.value.event_name && request.value.event_id) {
      try {
        const ev = await eventService.getEvent(request.value.event_id)
        request.value.event_name = ev.name
      } catch (e) {
        // ignore
      }
    }
  } catch (e) {
    error.value = 'Failed to load request'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>