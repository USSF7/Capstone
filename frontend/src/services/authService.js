import api from './api'

/**
 * Service responsible for authentication-related API calls.
 * 
 * @class AuthService
 */
class AuthService {
  /**
   * Registers a new user account.
   *
   * @param {string} name - Full name of the user
   * @param {string} email - Email address for registration
   * @param {string} password - Plain-text password
   * 
   * @returns {Promise<any>} Server response (user data or tokens)
   */
  async register(name, email, password) {
    return api.post('/auth/register', { name, email, password })
  }

  /**
   * Logs in a user and returns authentication tokens.
   *
   * @param {string} email - User email
   * @param {string} password - User password
   * 
   * @returns {Promise<any>} Server response containing access/refresh tokens
   */
  async login(email, password) {
    return api.post('/auth/login', { email, password })
  }

  /**
   * Refreshes the access token using the stored refresh token.
   *
   * @returns {Promise<any>} New authentication tokens
   */
  async refresh() {
    const refreshToken = localStorage.getItem('refresh_token')
    return api.request('/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
      },
    })
  }

  /**
   * Retrieves the currently authenticated user's profile.
   *
   * @returns {Promise<any>} User profile data
   */
  async getMe() {
    return api.get('/auth/me')
  }

  /**
   * Returns the backend Google OAuth login URL.
   *
   * @returns {string} OAuth login URL
   */
  getGoogleLoginUrl() {
    return 'http://localhost:5000/api/auth/google'
  }
}

export default new AuthService()
