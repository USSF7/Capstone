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
/**
 * A component that displays the messaging feed between the vendor and the renter, and it allows the vendor and the renter to send messages to each other.
 * @module MessageBox
 */

import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import messageService from '../../services/messageService'

/**
 * Interval for polling in milliseconds.
 * @type {number}
 * @constant
 */
const POLL_INTERVAL_MS = 3000

/**
 * Props for the component
 * @typedef {Object} Props
 * @property {string} [title="Messages"] - Title displayed in the UI
 * @property {number} currentUserId - ID of the current user (required)
 * @property {number|null} [otherUserId=null] - ID of the other user in the conversation
 * @property {number|null} [rentalId=null] - Associated rental ID
 */

/** @type {Props} */
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

/**
 * Emits the send event from this component.
 * @type {(event: 'sent') => void}
 */
const emit = defineEmits(['sent'])

/**
 * DOM reference to the message list container.
 * Used for scroll management.
 * @type {import('vue').Ref<HTMLElement|null>}
 */
const listEl = ref(null)

/**
 * Array of messages in the current conversation.
 * @type {import('vue').Ref<Array<any>>}
 */
const messages = ref([])

/**
 * Current message draft input by the user.
 * @type {import('vue').Ref<string>}
 */
const draft = ref('')

/**
 * Loading state when fetching messages.
 * @type {import('vue').Ref<boolean>}
 */
const loading = ref(false)

/**
 * Message send operation in progress.
 * @type {import('vue').Ref<boolean>}
 */
const sending = ref(false)

/**
 * Holds error message for user interface display.
 * @type {import('vue').Ref<string>}
 */
const error = ref('')

/**
 * Prevents overlapping fetch requests during polling.
 * @type {import('vue').Ref<boolean>}
 */
const isRefreshing = ref(false)

/**
 * Stores the polling interval ID.
 * @type {import('vue').Ref<number|null>}
 */
const pollTimer = ref(null)

/**
 * Gets the recipient user ID.
 */
const activeRecipientId = computed(() => toInt(props.otherUserId))

/**
 * Determines whether the conversation is tied to a rental.
 */
const isRentalThread = computed(() => Number.isInteger(props.rentalId))

/**
 * Determines if the app has the proper user and rental data to load and send messages.
 */
const readyToChat = computed(() => {
	return Number.isInteger(props.currentUserId) && Number.isInteger(activeRecipientId.value) && isRentalThread.value
})

/**
 * Safely converts a value to an integer. Returns null if invalid.
 *
 * @param {any} value - The integer value in a different format.
 * @returns {number|null} The integer value as a Number type.
 */
function toInt(value) {
	const intValue = Number(value)
	if (!Number.isFinite(intValue)) return null
	if (intValue <= 0) return null
	return Math.trunc(intValue)
}

/**
 * Builds optional parameters for conversation API calls. Includes rentalId only when relevant.
 *
 * @returns {{ rentalId: number|null }} The rental ID as a Number type.
 */
function getConversationOptions() {
	return {
		rentalId: isRentalThread.value ? props.rentalId : null,
	}
}

/**
 * Formats an ISO date string into a localized string.
 *
 * @param {string} isoDate - The iso formatted date.
 * @returns {string} Presentable formatted date.
 */
function formatDateTime(isoDate) {
	if (!isoDate) return ''
	return new Date(isoDate).toLocaleString()
}

/**
 * Scrolls the message list to the bottom after the application updates.
 */
async function scrollToBottom() {
	await nextTick()
	if (listEl.value) {
		listEl.value.scrollTop = listEl.value.scrollHeight
	}
}

/**
 * Determines whether the user is near the bottom of the message list.
 *
 * @returns {boolean} True if the user is near the bottom of the message list. False otherwise.
 */
function isNearBottom() {
	if (!listEl.value) return true
	const threshold = 48
	const distanceFromBottom = listEl.value.scrollHeight - listEl.value.scrollTop - listEl.value.clientHeight
	return distanceFromBottom <= threshold
}

/**
 * Loads messages for the current conversation.
 *
 * @param {{ silent?: boolean }} [options] - silent: Skips loading and error user interface updates when set to true.
 */
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

/**
 * Stops polling for new messages.
 */
function stopPolling() {
	if (pollTimer.value) {
		clearInterval(pollTimer.value)
		pollTimer.value = null
	}
}

/**
 * Starts polling for new messages at a fixed interval.
 */
function startPolling() {
	stopPolling()
	pollTimer.value = setInterval(() => {
		loadMessages({ silent: true })
	}, POLL_INTERVAL_MS)
}

/**
 * Sends a new message to the conversation. Clears the draft and refreshes messages on success.
 */
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

/**
 * Reloads messages when relevant props change.
 */
watch(
	() => [props.currentUserId, props.otherUserId, props.rentalId],
	() => {
		loadMessages({ silent: true })
	},
	{ immediate: true }
)

/**
 * Starts or stops polling depending on readiness state.
 */
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

/**
 * Cleanup polling when component is destroyed.
 */
onUnmounted(() => {
	stopPolling()
})
</script>
 