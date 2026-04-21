import api from './api'

/**
 * Service for handling user-related API operations.
 *
 * @class UserService
 */
class UserService {
  /**
   * Retrieves all users.
   *
   * @returns {Promise<Object>} List of users.
   */
  async getUsers() {
    return api.get('/users')
  }

  /**
   * Retrieves a single user by ID.
   *
   * @param {number|string} id - User ID.
   * @returns {Promise<Object>} User object.
   */
  async getUser(id) {
    return api.get(`/users/${id}`)
  }

  /**
   * Retrieves all messages associated with a user.
   *
   * @param {number|string} id - User ID.
   * @returns {Promise<Object>} List of user messages.
   */
  async getUserMessages(id) {
    return api.get(`/users/${id}/messages`)
  }

  /**
   * Creates a new user account.
   *
   * @param {string} name - Full name.
   * @param {string} email - Email address.
   * @param {string} password - Account password.
   * @param {string} phone - Phone number.
   * @param {string} date_of_birth - Date of birth.
   * @param {string} street_address - Street address.
   * @param {string} city - City.
   * @param {string} state - State.
   * @param {string} zip_code - ZIP code.
   * @param {boolean} vendor - Whether the user is a vendor.
   * @param {boolean} renter - Whether the user is a renter.
   * @param {string|null} picture - Profile picture URL.
   * @returns {Promise<Object>} Created user object.
   */
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

  /**
   * Creates a new user account.
   *
   * @param {string} name - Full name.
   * @param {string} email - Email address.
   * @param {string} password - Account password.
   * @param {string} phone - Phone number.
   * @param {string} date_of_birth - Date of birth.
   * @param {string} street_address - Street address.
   * @param {string} city - City.
   * @param {string} state - State.
   * @param {string} zip_code - ZIP code.
   * @param {boolean} vendor - Whether the user is a vendor.
   * @param {boolean} renter - Whether the user is a renter.
   * @param {string|null} picture - Profile picture  URL.
   * @returns {Promise<Object>} Created user object.
   */
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

  /**
   * Deletes a user by ID.
   *
   * @param {number|string} id - User ID.
   * @returns {Promise<Object>} Deletion response.
   */
  async deleteUser(id) {
    return api.delete(`/users/${id}`)
  }

  /**
   * Uploads a profile picture for a user.
   *
   * @param {File} userPicture - Image file to upload.
   * @returns {Promise<Object>} Uploaded file URL path.
   */
  async uploadUserPicture(userPicture) {
    const formData = new FormData()
    formData.append('picture_file', userPicture)

    return api.postForm('/users/picture', formData)
  }

  /**
   * Deletes an uploaded user profile picture from storage.
   *
   * @param {string} pictureFilePath - File path of the image to delete.
   * @returns {Promise<Object>} Deletion response.
   */
  async deleteUploadedUserPicture(pictureFilePath) {
    return api.delete('/users/picture/delete', {
      filepath: pictureFilePath
    })
  }
}

export default new UserService()