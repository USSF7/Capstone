import api from './api'

class AuthService {
  async register(name, email, password) {
    return api.post('/auth/register', { name, email, password })
  }

  async login(email, password) {
    return api.post('/auth/login', { email, password })
  }

  async refresh() {
    const refreshToken = localStorage.getItem('refresh_token')
    return api.request('/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
      },
    })
  }

  async getMe() {
    return api.get('/auth/me')
  }

  getGoogleLoginUrl() {
    return 'http://localhost:5000/api/auth/google'
  }
}

export default new AuthService()
