import apiClient from './client'
import type { HealthcareProfessionalResponse } from '../types'

export const professionalsApi = {
  list: (skip = 0, limit = 100) =>
    apiClient
      .get<{ total: number; professionals: HealthcareProfessionalResponse[] }>('/professionals', { params: { skip, limit } })
      .then((r) => r.data),

  get: (uuid: string) =>
    apiClient.get<HealthcareProfessionalResponse>(`/professionals/${uuid}`).then((r) => r.data),

  create: (data: Partial<HealthcareProfessionalResponse>) =>
    apiClient.post<HealthcareProfessionalResponse>('/professionals', data).then((r) => r.data),

  update: (uuid: string, data: Partial<HealthcareProfessionalResponse>) =>
    apiClient.patch<HealthcareProfessionalResponse>(`/professionals/${uuid}`, data).then((r) => r.data),

  delete: (uuid: string) =>
    apiClient.delete(`/professionals/${uuid}`),
}
