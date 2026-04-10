<template>
	<div class="h-[32rem] max-h-[70vh] min-h-0 flex flex-col border border-gray-200 rounded-lg overflow-hidden bg-white">
		<div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
			<h4 class="font-semibold text-gray-800">{{ title }}</h4>
			<p class="text-sm text-gray-600" v-if="!readyToChat">
				Select a user and rental to start messaging.
			</p>
			<p class="text-sm text-gray-600" v-else-if="isRentalThread">
				Rental thread
			</p>
		</div>

		<div ref="listEl" class="flex-1 min-h-0 overflow-y-auto p-3 space-y-2 bg-slate-50">
			<p v-if="loading" class="text-sm text-gray-600">Loading messages...</p>
			<p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
			<p v-else-if="messages.length === 0" class="text-sm text-gray-500">No messages yet.</p>

			<div
				v-for="message in messages"
				:key="message.id"
				:class="[
					'max-w-[80%] rounded-lg px-3 py-2 text-sm shadow-sm',
					message.sender_id === currentUserId
						? 'ml-auto bg-blue-600 text-white'
						: 'mr-auto bg-white text-gray-800 border border-gray-200'
				]"
			>
				<p class="whitespace-pre-wrap break-words">{{ message.data }}</p>
				<p
					:class="[
						'mt-1 text-[11px]',
						message.sender_id === currentUserId ? 'text-blue-100' : 'text-gray-500'
					]"
				>
					{{ formatDateTime(message.send_time) }}
				</p>
			</div>
		</div>

		<form class="p-3 border-t border-gray-200 bg-white" @submit.prevent="sendMessage">
			<div class="flex gap-2">
				<textarea
					v-model="draft"
					rows="2"
					class="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
					:placeholder="readyToChat ? 'Type your message...' : 'Select a user and rental first'"
					:disabled="!readyToChat || sending"
					@keydown.enter.exact.prevent="sendMessage"
				/>
				<button
					type="submit"
					class="px-4 py-2 rounded-md text-white font-medium"
					:class="readyToChat && !sending ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400 cursor-not-allowed'"
					:disabled="!readyToChat || sending"
				>
					{{ sending ? 'Sending...' : 'Send' }}
				</button>
			</div>
		</form>
	</div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import messageService from '../../services/messageService'

const POLL_INTERVAL_MS = 3000

const props = defineProps({
	title: {
		type: String,
		default: 'Messages',
	},
	currentUserId: {
		type: Number,
		required: true,
	},
	otherUserId: {
		type: Number,
		default: null,
	},
	rentalId: {
		type: Number,
		default: null,
	},
})

const emit = defineEmits(['sent'])

const listEl = ref(null)
const messages = ref([])
const draft = ref('')
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const isRefreshing = ref(false)
const pollTimer = ref(null)

const activeRecipientId = computed(() => toInt(props.otherUserId))
const isRentalThread = computed(() => Number.isInteger(props.rentalId))
const readyToChat = computed(() => {
	return Number.isInteger(props.currentUserId) && Number.isInteger(activeRecipientId.value) && isRentalThread.value
})

function toInt(value) {
	const intValue = Number(value)
	if (!Number.isFinite(intValue)) return null
	if (intValue <= 0) return null
	return Math.trunc(intValue)
}

function getConversationOptions() {
	return {
		rentalId: isRentalThread.value ? props.rentalId : null,
	}
}

function formatDateTime(isoDate) {
	if (!isoDate) return ''
	return new Date(isoDate).toLocaleString()
}

async function scrollToBottom() {
	await nextTick()
	if (listEl.value) {
		listEl.value.scrollTop = listEl.value.scrollHeight
	}
}

function isNearBottom() {
	if (!listEl.value) return true
	const threshold = 48
	const distanceFromBottom = listEl.value.scrollHeight - listEl.value.scrollTop - listEl.value.clientHeight
	return distanceFromBottom <= threshold
}

async function loadMessages({ silent = false } = {}) {
	if (!readyToChat.value) {
		messages.value = []
		return
	}
	if (isRefreshing.value) return
	isRefreshing.value = true

	if (!silent) {
		loading.value = true
		error.value = ''
	}
	try {
		const wasNearBottom = isNearBottom()
		const previousCount = messages.value.length
		const nextMessages = await messageService.getConversation(props.currentUserId, activeRecipientId.value, getConversationOptions())
		messages.value = nextMessages

		if (!silent || (nextMessages.length > previousCount && wasNearBottom)) {
			await scrollToBottom()
		}
	} catch (e) {
		if (!silent) {
			error.value = e.message || 'Failed to load messages.'
		}
	} finally {
		if (!silent) {
			loading.value = false
		}
		isRefreshing.value = false
	}
}

function stopPolling() {
	if (pollTimer.value) {
		clearInterval(pollTimer.value)
		pollTimer.value = null
	}
}

function startPolling() {
	stopPolling()
	pollTimer.value = setInterval(() => {
		loadMessages({ silent: true })
	}, POLL_INTERVAL_MS)
}

async function sendMessage() {
	if (!readyToChat.value || !draft.value.trim()) return

	sending.value = true
	error.value = ''
	try {
		await messageService.createMessage(props.currentUserId, activeRecipientId.value, draft.value.trim(), getConversationOptions())
		draft.value = ''
		await loadMessages()
		emit('sent')
	} catch (e) {
		error.value = e.message || 'Failed to send message.'
	} finally {
		sending.value = false
	}
}

watch(
	() => [props.currentUserId, props.otherUserId, props.rentalId],
	() => {
		loadMessages({ silent: true })
	},
	{ immediate: true }
)

watch(
	() => readyToChat.value,
	(isReady) => {
		if (!isReady) {
			stopPolling()
			messages.value = []
			return
		}

		loadMessages()
		startPolling()
	},
	{ immediate: true }
)

onUnmounted(() => {
	stopPolling()
})
</script>
 