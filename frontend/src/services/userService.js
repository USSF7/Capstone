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

  async createUser(name, email, password, phone, date_of_birth, street_address, city, state, zip_code, vendor, renter, picture) {
    return api.post('/users', { 
      name: name,
      email: email,
      password: password, 
      phone: phone, 
      date_of_birth: date_of_birth, 
      street_address: street_address,
      city: city, 
      state: state, 
      zip_code: zip_code, 
      vendor: vendor, 
      renter: renter,
      picture: picture
    })
  }

  async updateUser(id, name, email, phone, date_of_birth, street_address, city, state, zip_code, vendor, renter, picture) {
    return api.put(`/users/${id}`, { 
      name: name, 
      email: email, 
      phone: phone, 
      date_of_birth: date_of_birth, 
      street_address: street_address, 
      city: city, 
      state: state, 
      zip_code: zip_code, 
      vendor: vendor, 
      renter: renter,
      picture: picture
    })
  }

  async deleteUser(id) {
    return api.delete(`/users/${id}`)
  }

  async uploadUserPicture(userPicture) {
    const formData = new FormData()
    formData.append('picture_file', userPicture)

    return api.postForm('/users/picture', formData)
  }

  async deleteUploadedUserPicture(pictureFilePath) {
    return api.delete('/users/picture/delete', {
      filepath: pictureFilePath
    })
  }
}

export default new UserService()