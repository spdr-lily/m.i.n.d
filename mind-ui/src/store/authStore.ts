import { create } from 'zustand'
import type { User, LoginRequest } from '../types'
import { authApi } from '../api/auth'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  login: (data: LoginRequest) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('mind_token'),
  loading: false,

  login: async (data) => {
    const { access_token } = await authApi.login(data)
    localStorage.setItem('mind_token', access_token)
    set({ token: access_token })
    const user = await authApi.me()
    set({ user })
  },

  logout: () => {
    localStorage.removeItem('mind_token')
    set({ user: null, token: null })
  },

  loadUser: async () => {
    const token = localStorage.getItem('mind_token')
    if (!token) return
    set({ loading: true })
    try {
      const user = await authApi.me()
      set({ user, loading: false })
    } catch {
      localStorage.removeItem('mind_token')
      set({ user: null, token: null, loading: false })
    }
  },
}))
