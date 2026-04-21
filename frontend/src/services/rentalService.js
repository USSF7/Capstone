import api from './api'

/**
 * Service for handling rental-related API operations.
 *
 * @class RentalService
 */
class RentalService {
  /**
   * Retrieves all rentals.
   *
   * @returns {Promise<Object>} List of all rentals.
   */
  async getRentals() {
    return api.get('/rentals')
  }

  /**
   * Retrieves a single rental by ID.
   *
   * @param {number|string} rentalId - Rental ID.
   * @returns {Promise<Object>} Rental object.
   */
  async getRental(rentalId) {
    return api.get(`/rentals/${rentalId}`)
  }

  /**
   * Retrieves a rental with its associated equipment.
   *
   * @param {number|string} rentalId - Rental ID.
   * @returns {Promise<Object>} Rental with equipment details.
   */
  async getRentalWithEquipment(rentalId) {
    return api.get(`/rentals/rental_equipment/${rentalId}`)
  }

  /**
   * Retrieves rentals for a specific renter.
   *
   * @param {number|string} renterId - Renter user ID.
   * @returns {Promise<Object>} List of rentals for the renter.
   */
  async getRentalsByRenter(renterId) {
    return api.get(`/rentals/renter/${renterId}`)
  }

  /**
   * Retrieves rentals for a renter including equipment details.
   *
   * @param {number|string} renterId - Renter user ID.
   * @returns {Promise<Object>} Rentals with equipment included.
   */
  async getRentalsWithEquipmentByRenter(renterId) {
    return api.get(`/rentals/renter_equipment/${renterId}`)
  }

  /**
   * Retrieves rentals for a specific vendor.
   *
   * @param {number|string} vendorId - Vendor user ID.
   * @returns {Promise<Object>} List of rentals for the vendor.
   */
  async getRentalsByVendor(vendorId) {
    return api.get(`/rentals/vendor/${vendorId}`)
  }

  /**
   * Retrieves rentals filtered by status.
   *
   * @param {string} status - Rental status.
   * @returns {Promise<Object>} List of rentals matching status.
   */
  async getRentalsByStatus(status) {
    return api.get(`/rentals/status/${status}`)
  }

  /**
   * Retrieves rentals for a vendor filtered by status.
   *
   * @param {number|string} vendorId - Vendor user ID.
   * @param {string} status - Rental status.
   * @returns {Promise<Object>} Filtered rentals.
   */
  async getRentalsByVendorAndStatus(vendorId, status) {
    return api.get(`/rentals/vendor/${vendorId}/status/${status}`)
  }

  /**
   * Creates a standard rental.
   *
   * @param {number|string} renterId - Renter user ID.
   * @param {number|string} vendorId - Vendor user ID.
   * @param {number} agreedPrice - Agreed rental price.
   * @param {string} startDate - Start datetime (ISO string).
   * @param {string} endDate - End datetime (ISO string).
   * @param {string} location - Meeting or pickup location.
   * @param {string} [status='requesting'] - Initial rental status.
   * @param {boolean} [deleted=false] - Soft delete flag.
   * @returns {Promise<Object>} Created rental object.
   */
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

  /**
   * Creates a rental request that includes selected equipment.
   *
   * @param {number|string} vendorId - Vendor user ID.
   * @param {number} agreedPrice - Agreed price.
   * @param {string} startDate - Start datetime (ISO string).
   * @param {string} endDate - End datetime (ISO string).
   * @param {string} location - Meeting location.
   * @param {Array<number|string>} [equipmentIds=[]] - Selected equipment IDs.
   * @param {number|null} [meetingLat=null] - Meeting latitude.
   * @param {number|null} [meetingLng=null] - Meeting longitude.
   * @returns {Promise<Object>} Created rental request.
   */
  async createRentalRequestWithEquipment(vendorId, agreedPrice, startDate, endDate, location, equipmentIds = [], meetingLat = null, meetingLng = null) {
    return api.post('/rentals', {
      vendor_id: vendorId,
      agreed_price: agreedPrice,
      start_date: startDate,
      end_date: endDate,
      location,
      equipment_ids: equipmentIds,
      meeting_lat: meetingLat,
      meeting_lng: meetingLng,
    })
  }

  /**
   * Gets equipment availability for a vendor within a date range.
   *
   * @param {number|string} vendorId - Vendor user ID.
   * @param {string} startDate - Start datetime.
   * @param {string} endDate - End datetime.
   * @returns {Promise<Object>} Equipment availability data.
   */
  async getVendorEquipmentAvailability(vendorId, startDate, endDate) {
    return api.get(`/rentals/vendor/${vendorId}/equipment-availability?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`)
  }

  /**
   * Updates a rental's main fields.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {string} status - New status.
   * @param {string} location - Updated location.
   * @param {number} agreedPrice - Updated price.
   * @param {boolean} deleted - Soft delete flag.
   * @param {boolean} [approve=false] - Approval flag.
   * @returns {Promise<Object>} Updated rental.
   */
  async updateRental(rentalId, status, location, agreedPrice, deleted, approve = false) {
    return api.put(`/rentals/${rentalId}`, {
      status,
      location,
      agreed_price: agreedPrice,
      deleted,
      approve,
    })
  }

  /**
   * Marks whether the renter has reviewed the rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {boolean} renterReviewedStatus - Review status.
   * @returns {Promise<Object>} Updated rental.
   */
  async switchRenterReviewedStatus(rentalId, renterReviewedStatus) {
    return api.put(`/rentals/switch-renter-review-status/${rentalId}`, {
      renter_review_status: Boolean(renterReviewedStatus)
    })
  }

  /**
   * Marks whether the vendor has reviewed the rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {boolean} vendorReviewedStatus - Review status.
   * @returns {Promise<Object>} Updated rental.
   */
  async switchVendorReviewedStatus(rentalId, vendorReviewedStatus) {
    return api.put(`/rentals/switch-vendor-review-status/${rentalId}`, {
      vendor_review_status: Boolean(vendorReviewedStatus)
    })
  }

  /**
   * Marks whether a specific equipment item has been reviewed.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {number|string} equipmentId - Equipment ID.
   * @param {boolean} equipmentReviewedStatus - Review status.
   * @returns {Promise<Object>} Updated rental.
   */
  async switchEquipmentReviewedStatus(rentalId, equipmentId, equipmentReviewedStatus) {
    return api.put(`/rentals/switch-equipment-review-status/${rentalId}`, {
      equipment_id: Number(equipmentId),
      equipment_review_status: Boolean(equipmentReviewedStatus)
    })
  }

  /**
   * Updates rental details using a flexible payload.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {Object} payload - Fields to update.
   * @returns {Promise<Object>} Updated rental.
   */
  async updateRentalDetails(rentalId, payload) {
    return api.put(`/rentals/${rentalId}`, payload)
  }

  /**
   * Deletes a rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @returns {Promise<Object>} Deletion response.
   */
  async deleteRental(rentalId) {
    return api.delete(`/rentals/${rentalId}`)
  }

  /**
   * Gets the average rental price for an equipment type in a location.
   *
   * @param {string} equipmentName - Equipment name.
   * @param {string} location - Location string.
   * @returns {Promise<Object>} Average price data.
   */
  async getAveragePrice(equipmentName, location) {
    return api.get(`/rentals/average-price?equipment_name=${encodeURIComponent(equipmentName)}&location=${encodeURIComponent(location)}`)
  }
}

export default new RentalService()
