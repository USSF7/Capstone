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

  async getConversation(userId1, userId2) {
    return api.get(`/messages/conversation/${userId1}/${userId2}`)
  }

  async createMessage(senderId, receiverId, data) {
    return api.post('/messages', {
      sender_id: senderId,
      receiver_id: receiverId,
      data,
    })
  }

  async deleteMessage(messageId) {
    return api.delete(`/messages/${messageId}`)
  }
}

export default new MessageService()
