import api from './index'

export const authApi = {
  async login(username: string, password: string) {
    const { data } = await api.post('/auth/login', { username, password })
    return data as { access_token: string; refresh_token: string; token_type: string }
  },

  async register(username: string, password: string, confirmPassword: string) {
    const { data } = await api.post('/auth/register', {
      username,
      password,
      confirm_password: confirmPassword,
    })
    return data
  },

  async getMe() {
    const { data } = await api.get('/auth/me')
    return data
  },

  async logout() {
    await api.post('/auth/logout')
  },
}
