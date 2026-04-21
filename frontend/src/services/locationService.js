import api from './api'

/**
 * Service for handling location-related backend operations.
 *
 * @class LocationService
 */
class LocationService {
  /**
   * Retrieves the Google Maps API key from the backend.
   *
   * @returns {Promise<Object>} Response containing the maps API key.
   */
  async getMapsKey() {
    return api.get('/location/maps-key')
  }

  /**
   * Geocodes a structured address into latitude/longitude coordinates.
   *
   * @param {string} streetAddress - Street address.
   * @param {string} city - City name.
   * @param {string} state - State or province.
   * @param {string} zipCode - Postal/ZIP code.
   * @returns {Promise<Object>} Geocoding result with coordinates and metadata.
   */
  async geocode(streetAddress, city, state, zipCode) {
    return api.post('/location/geocode', {
      street_address: streetAddress,
      city,
      state,
      zip_code: zipCode,
    })
  }

  /**
   * Geocodes a freeform address string into coordinates.
   *
   * @param {string} address - Full address string entered by the user.
   * @returns {Promise<Object>} Geocoding result with latitude and longitude.
   */
  async geocodeFreeform(address) {
    return api.post('/location/geocode-freeform', { address })
  }

  /**
   * Searches for equipment near a geographic coordinate.
   *
   * @param {number} lat - Latitude of search center.
   * @param {number} lng - Longitude of search center.
   * @param {number} [radius=25] - Search radius in kilometers.
   * @param {string|null} [name=null] - Optional equipment name filter.
   * @returns {Promise<Object>} List of nearby equipment results.
   */
  async searchEquipmentNearby(lat, lng, radius = 25, name = null) {
    let url = `/location/equipment/search?lat=${lat}&lng=${lng}&radius=${radius}`
    if (name) url += `&name=${encodeURIComponent(name)}`
    return api.get(url)
  }

  /**
   * Retrieves suggested meeting locations for a rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @returns {Promise<Object>} Suggested meeting locations.
   */
  async getMeetingSuggestions(rentalId) {
    return api.get(`/location/rental/${rentalId}/meeting-suggestions`)
  }

  /**
   * Retrieves meeting location suggestions between two geographic points.
   *
   * @param {number} renterLat - Renter latitude.
   * @param {number} renterLng - Renter longitude.
   * @param {number} vendorLat - Vendor latitude.
   * @param {number} vendorLng - Vendor longitude.
   * @returns {Promise<Object>} Suggested meeting locations between both users.
   */
  async getMeetingSuggestionsForPoints(renterLat, renterLng, vendorLat, vendorLng) {
    return api.get(
      `/location/meeting-suggestions?renter_lat=${encodeURIComponent(renterLat)}&renter_lng=${encodeURIComponent(renterLng)}&vendor_lat=${encodeURIComponent(vendorLat)}&vendor_lng=${encodeURIComponent(vendorLng)}`
    )
  }

  /**
   * Sets the meeting location for a rental.
   *
   * @param {number|string} rentalId - Rental ID.
   * @param {Object} placeData - Location payload.
   * @returns {Promise<Object>} Updated rental/location response.
   */
  async setMeetingLocation(rentalId, placeData) {
    return api.post(`/location/rental/${rentalId}/meeting-location`, placeData)
  }
}

export default new LocationService()
