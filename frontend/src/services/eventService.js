import api from './api'

class EventService {
  async getEvents() {
    return api.get('/events')
  }

  async getEvent(eventId) {
    return api.get(`/events/${eventId}`)
  }

  async getEventsByUser(userId) {
    return api.get(`/events/user/${userId}`)
  }

  async createEvent(userId, name, date) {
    return api.post('/events', { user_id: userId, name, date })
  }

  async updateEvent(eventId, name, date) {
    return api.put(`/events/${eventId}`, { name, date })
  }

  async deleteEvent(eventId) {
    return api.delete(`/events/${eventId}`)
  }
}

export default new EventService()
