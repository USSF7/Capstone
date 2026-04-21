import api from './api'

/**
 * Service for handling messaging functionality between users.
 *
 * @class MessageService
 */
class MessageService {
  /**
   * Retrieves all messages.
   *
   * @returns {Promise<Object>} List of all messages.
   */
  async getMessages() {
    return api.get('/messages')
  }

  /**
   * Retrieves a single message by its ID.
   *
   * @param {number|string} messageId - The message ID.
   * @returns {Promise<Object>} Message object.
   */
  async getMessage(messageId) {
    return api.get(`/messages/${messageId}`)
  }

  /**
   * Retrieves the inbox for a specific user.
   *
   * @param {number|string} userId - The recipient user ID.
   * @returns {Promise<Object>} List of received messages.
   */
  async getInbox(userId) {
    return api.get(`/messages/inbox/${userId}`)
  }

  /**
   * Retrieves messages sent by a specific user.
   *
   * @param {number|string} senderId - The sender user ID.
   * @returns {Promise<Object>} List of sent messages.
   */
  async getSentMessages(senderId) {
    return api.get(`/messages/sent/${senderId}`)
  }

  /**
   * Retrieves a conversation between two users.
   *
   * @param {number|string} userId1 - First user ID.
   * @param {number|string} userId2 - Second user ID.
   * @param {Object} [options={}] - Optional filters.
   * @param {number|string} [options.rentalId] - Rental ID to filter messages by rental context.
   * @returns {Promise<Object>} Conversation messages between the two users.
   */
  async getConversation(userId1, userId2, options = {}) {
    const params = new URLSearchParams()

    if (options.rentalId != null) {
      params.append('rental_id', options.rentalId)
    }

    const query = params.toString()
    return api.get(`/messages/conversation/${userId1}/${userId2}${query ? `?${query}` : ''}`)
  }

  /**
   * Retrieves all messages associated with a rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @returns {Promise<Object>} List of rental-related messages.
   */
  async getMessagesByRental(rentalId) {
    return api.get(`/messages/rental/${rentalId}`)
  }

  /**
   * Creates and sends a new message.
   *
   * @param {number|string} senderId - Sender user ID.
   * @param {number|string} receiverId - Receiver user ID.
   * @param {string} data - Message content/body.
   * @param {Object} [options={}] - Optional metadata.
   * @param {number|string|null} [options.rentalId] - Optional rental ID association.
   * @returns {Promise<Object>} Created message object.
   */
  async createMessage(senderId, receiverId, data, options = {}) {
    return api.post('/messages', {
      sender_id: senderId,
      receiver_id: receiverId,
      data,
      rental_id: options.rentalId ?? null,
    })
  }

  /**
   * Deletes a message by ID.
   *
   * @param {number|string} messageId - Message ID to delete.
   * @returns {Promise<Object>} Deletion response.
   */
  async deleteMessage(messageId) {
    return api.delete(`/messages/${messageId}`)
  }
}

export default new MessageService()
