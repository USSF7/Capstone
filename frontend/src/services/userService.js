import api from './api'

class UserService {
  async getUsers() {
    return api.get('/users')
  }

  async getUser(id) {
    return api.get(`/users/${id}`)
  }

  async getUserMessages(id) {
    return api.get(`/users/${id}/messages`)
  }

  async createUser(name, email) {
    return api.post('/users', { name, email })
  }

  async updateUser(id, name, email) {
    return api.put(`/users/${id}`, { name, email })
  }

  async deleteUser(id) {
    return api.delete(`/users/${id}`)
  }
}

export default new UserService()