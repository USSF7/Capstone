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

  async createEquipment(ownerId, name) {
    return api.post('/equipment', { owner_id: ownerId, name })
  }

  async updateEquipment(equipmentId, name, ownerId) {
    return api.put(`/equipment/${equipmentId}`, { name, owner_id: ownerId })
  }

  async deleteEquipment(equipmentId) {
    return api.delete(`/equipment/${equipmentId}`)
  }
}

export default new EquipmentService()
