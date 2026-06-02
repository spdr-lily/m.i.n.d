import apiClient from './client'
import type { HealthcareProfessionalResponse } from '../types'

export const professionalsApi = {
  list: (skip = 0, limit = 100) =>
    apiClient
      .get<{ total: number; professionals: HealthcareProfessionalResponse[] }>('/professionals', { params: { skip, limit } })
      .then((r) => r.data),
}
