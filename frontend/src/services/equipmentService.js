import api from './api'

/**
 * Service for handling equipment-related API operations.
 * 
 * @class EquipmentService
 */
class EquipmentService {
  /**
   * Retrieves all equipment.
   *
   * @returns {Promise<any>} List of all equipment
   */
  async getEquipment() {
    return api.get('/equipment')
  }

  /**
   * Retrieves a single equipment item by ID.
   *
   * @param {number|string} equipmentId - Unique equipment identifier
   * @returns {Promise<any>} Equipment details
   */
  async getEquipmentById(equipmentId) {
    return api.get(`/equipment/${equipmentId}`)
  }

  /**
   * Retrieves all equipment owned by a specific user.
   *
   * @param {number|string} ownerId - User ID of the owner
   * @returns {Promise<any>} List of equipment owned by the user
   */
  async getEquipmentByOwner(ownerId) {
    return api.get(`/equipment/owner/${ownerId}`)
  }

  /**
   * Retrieves all equipment owned by a user including rental data.
   *
   * @param {number|string} ownerId - User ID of the owner
   * @returns {Promise<any>} Equipment list with rental relationships
   */
  async getEquipmentByOwnerWithRentals(ownerId) {
    return api.get(`/equipment/owner/${ownerId}/with-rentals`)
  }

  /**
   * Creates a new equipment listing.
   *
   * @param {number|string} ownerId - ID of the equipment owner
   * @param {string} name - Equipment name
   * @param {number} price - Rental price
   * @param {string} description - Equipment description
   * @param {string} picture - Image path or URL
   * @param {string} condition - Condition of the equipment
   * 
   * @returns {Promise<any>} Created equipment object
   */
  async createEquipment(ownerId, name, price, description, picture, condition) {
    return api.post('/equipment', {
      owner_id: ownerId,
      name,
      price,
      description,
      picture,
      condition
    })
  }

  /**
   * Updates an existing equipment listing.
   *
   * @param {number|string} equipmentId - Equipment ID
   * @param {string} name - Updated name
   * @param {number|string} ownerId - Owner ID
   * @param {number} price - Updated price
   * @param {string} description - Updated description
   * @param {string} picture - Updated picture path or URL
   * @param {string} condition - Updated condition
   * 
   * @returns {Promise<any>} Updated equipment object
   */
  async updateEquipment(equipmentId, name, ownerId, price, description, picture, condition) {
    return api.put(`/equipment/${equipmentId}`, {
      name,
      owner_id: ownerId,
      price,
      description,
      picture,
      condition
    })
  }

  /**
   * Uploads an equipment image file.
   *
   * @param {File} equipmentPicture - Image file to upload
   * @returns {Promise<any>} Uploaded file path
   */
  async uploadEquipmentPicture(equipmentPicture) {
    const formData = new FormData()
    formData.append('picture_file', equipmentPicture)

    return api.postForm('/equipment/picture', formData)
  }

  /**
   * Deletes an uploaded equipment image from storage.
   *
   * @param {string} pictureFilePath - Server file path of the image
   * @returns {Promise<any>} Deletion confirmation response
   */
  async deleteUploadedEquipmentPicture(pictureFilePath) {
    return api.delete('/equipment/picture/delete', {
      filepath: pictureFilePath
    })
  }

  /**
   * Deletes an equipment listing.
   *
   * @param {number|string} equipmentId - Equipment ID to delete
   * @returns {Promise<any>} Deletion confirmation response
   */
  async deleteEquipment(equipmentId) {
    return api.delete(`/equipment/${equipmentId}`)
  }

  /**
   * Retrieves only equipment names.
   *
   * @returns {Promise<any>} List of equipment names
   */
  async getEquipmentNames() {
    return api.get('/equipment/names')
  }
}

export default new EquipmentService()
