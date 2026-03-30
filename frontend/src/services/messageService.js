import api from './api'

class MessageService {
  async getMessages() {
    return api.get('/messages')
  }

  async getMessage(messageId) {
    return api.get(`/messages/${messageId}`)
  }

  async getInbox(userId) {
    return api.get(`/messages/inbox/${userId}`)
  }

  async getSentMessages(senderId) {
    return api.get(`/messages/sent/${senderId}`)
  }

  async getConversation(userId1, userId2, options = {}) {
    const params = new URLSearchParams()

    if (options.rentalId != null) {
      params.append('rental_id', options.rentalId)
    }

    const query = params.toString()
    return api.get(`/messages/conversation/${userId1}/${userId2}${query ? `?${query}` : ''}`)
  }

  async getMessagesByRental(rentalId) {
    return api.get(`/messages/rental/${rentalId}`)
  }

  async createMessage(senderId, receiverId, data, options = {}) {
    return api.post('/messages', {
      sender_id: senderId,
      receiver_id: receiverId,
      data,
      rental_id: options.rentalId ?? null,
    })
  }

  async deleteMessage(messageId) {
    return api.delete(`/messages/${messageId}`)
  }
}

export default new MessageService()
