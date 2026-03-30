import api from './api'

class LocationService {
  async getMapsKey() {
    return api.get('/location/maps-key')
  }

  async geocode(streetAddress, city, state, zipCode) {
    return api.post('/location/geocode', {
      street_address: streetAddress,
      city,
      state,
      zip_code: zipCode,
    })
  }

  async searchEquipmentNearby(lat, lng, radius = 25, name = null) {
    let url = `/location/equipment/search?lat=${lat}&lng=${lng}&radius=${radius}`
    if (name) url += `&name=${encodeURIComponent(name)}`
    return api.get(url)
  }

  async getMeetingSuggestions(rentalId) {
    return api.get(`/location/rental/${rentalId}/meeting-suggestions`)
  }

  async setMeetingLocation(rentalId, placeData) {
    return api.post(`/location/rental/${rentalId}/meeting-location`, placeData)
  }
}

export default new LocationService()
