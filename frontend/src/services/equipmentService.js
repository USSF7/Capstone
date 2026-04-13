import api from './api'

class EquipmentService {
  async getEquipment() {
    return api.get('/equipment')
  }

  async getEquipmentById(equipmentId) {
    return api.get(`/equipment/${equipmentId}`)
  }

  async getEquipmentByOwner(ownerId) {
    return api.get(`/equipment/owner/${ownerId}`)
  }

  async getEquipmentByOwnerWithRentals(ownerId) {
    return api.get(`/equipment/owner/${ownerId}/with-rentals`)
  }

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

  async uploadEquipmentPicture(equipmentPicture) {
    const formData = new FormData()
    formData.append('picture_file', equipmentPicture)

    return api.postForm('/equipment/picture', formData)
  }

  async deleteUploadedEquipmentPicture(pictureFilePath) {
    return api.delete('/equipment/picture/delete', {
      filepath: pictureFilePath
    })
  }

  async deleteEquipment(equipmentId) {
    return api.delete(`/equipment/${equipmentId}`)
  }

  async getEquipmentNames() {
    return api.get('/equipment/names')
  }
}

export default new EquipmentService()
