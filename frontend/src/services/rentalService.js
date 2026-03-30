import api from './api'

class RentalService {
  async getRentals() {
    return api.get('/rentals')
  }

  async getRental(rentalId) {
    return api.get(`/rentals/${rentalId}`)
  }

  async getRentalWithEquipment(rentalId) {
    return api.get(`/rentals/rental_equipment/${rentalId}`)
  }

  async getRentalsByRenter(renterId) {
    return api.get(`/rentals/renter/${renterId}`)
  }

  async getRentalsWithEquipmentByRenter(renterId) {
    return api.get(`/rentals/renter_equipment/${renterId}`)
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

  async createRental(renterId, vendorId, agreedPrice, startDate, endDate, location, status = 'requesting', deleted = false) {
    return api.post('/rentals', {
      renter_id: renterId,
      vendor_id: vendorId,
      agreed_price: agreedPrice,
      start_date: startDate,
      end_date: endDate,
      location,
      status,
      deleted,
    })
  }

  async updateRental(rentalId, status, location, agreedPrice, deleted) {
    return api.put(`/rentals/${rentalId}`, {
      status,
      location,
      agreed_price: agreedPrice,
      deleted,
    })
  }

  async deleteRental(rentalId) {
    return api.delete(`/rentals/${rentalId}`)
  }

  async getAveragePrice(equipmentName, location) {
    return api.get(`/rentals/average-price?equipment_name=${encodeURIComponent(equipmentName)}&location=${encodeURIComponent(location)}`)
  }
}

export default new RentalService()
