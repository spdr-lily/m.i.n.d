import apiClient from './client'
import type { LoginRequest, TokenResponse, User, RegisterRequest } from '../types'

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>('/auth/login', data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<User>('/auth/register', data).then((r) => r.data),

  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),
}
