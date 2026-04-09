import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.user?.username || '',
    role: (state) => state.user?.role || '',
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    setUser(user) {
      this.user = user
    },
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    logout() {
      this.user = null
      this.setToken(null)
    },
  },
})
