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

  async createRequest(requesterId, eventId, name, maxPrice, count, startDate, endDate, location = null, minPrice = null, comments = null) {
    return api.post('/requests', {
      requester_id: requesterId,
      event_id: eventId,
      name,
      max_price: maxPrice,
      min_price: minPrice,
      count,
      start_date: startDate,
      end_date: endDate,
      location: location,
      comments: comments
    })
  }

  async updateRequest(requestId, data) {
    // data should contain any of the updatable fields.  The backend
    // accepts name, event_id, location, start_date, end_date,
    // max_price, count and optionally status.
    return api.put(`/requests/${requestId}`, data)
  }

  async deleteRequest(requestId) {
    return api.delete(`/requests/${requestId}`)
  }

  async getRecommendationsByRenter(renterId) {
    // TODO implement this endpoint in the backend and update this function accordingly
    // For now, this is just a placeholder that returns all requests.  The frontend can filter these as needed.
    return api.get(`/requests`)
  }
}

export default new RequestService()
