import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const username = ref(localStorage.getItem('username') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(user: string, password: string) {
    const res = await authApi.login(user, password)
    token.value = res.access_token
    refreshToken.value = res.refresh_token
    username.value = user
    localStorage.setItem('access_token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
    localStorage.setItem('username', user)
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    username.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('username')
  }

  return { token, refreshToken, username, isLoggedIn, login, logout }
})
