import api from './api'

class RequestService {
  async getRequests() {
    return api.get('/requests')
  }

  async getRequest(requestId) {
    return api.get(`/requests/${requestId}`)
  }

  async getRequestsByRequester(requesterId) {
    return api.get(`/requests/requester/${requesterId}`)
  }

  async getRequestsByEvent(eventId) {
    return api.get(`/requests/event/${eventId}`)
  }

  async getRequestsByStatus(status) {
    return api.get(`/requests/status/${status}`)
  }

  async createRequest(requesterId, eventId, name, maxPrice, count, startDate, endDate) {
    return api.post('/requests', {
      requester_id: requesterId,
      event_id: eventId,
      name,
      max_price: maxPrice,
      count,
      start_date: startDate,
      end_date: endDate,
    })
  }

  async updateRequest(requestId, status, maxPrice, count) {
    return api.put(`/requests/${requestId}`, {
      status,
      max_price: maxPrice,
      count,
    })
  }

  async deleteRequest(requestId) {
    return api.delete(`/requests/${requestId}`)
  }
}

export default new RequestService()
