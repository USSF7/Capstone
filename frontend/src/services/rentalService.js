import api from './api'

class RentalService {
  async getRentals() {
    return api.get('/rentals')
  }

  async getRental(rentalId) {
    return api.get(`/rentals/${rentalId}`)
  }

  async getRentalsByRenter(renterId) {
    return api.get(`/rentals/renter/${renterId}`)
  }

  async getRentalsByVendor(vendorId) {
    return api.get(`/rentals/vendor/${vendorId}`)
  }

  async getRentalsByStatus(status) {
    return api.get(`/rentals/status/${status}`)
  }

  async getRentalsByVendorAndStatus(vendorId, status) {
    return api.get(`/rentals/vendor/${vendorId}/status/${status}`)
  }

  async createRental(renterId, vendorId, agreedPrice, startDate, endDate, eventId, location) {
    return api.post('/rentals', {
      renter_id: renterId,
      vendor_id: vendorId,
      agreed_price: agreedPrice,
      start_date: startDate,
      end_date: endDate,
      event_id: eventId,
      location,
    })
  }

  async updateRental(rentalId, status, location, agreedPrice) {
    return api.put(`/rentals/${rentalId}`, {
      status,
      location,
      agreed_price: agreedPrice,
    })
  }

  async deleteRental(rentalId) {
    return api.delete(`/rentals/${rentalId}`)
  }
}

export default new RentalService()
