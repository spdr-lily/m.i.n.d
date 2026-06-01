import apiClient from './client'
import type { Alert } from '../types'

export const alertsApi = {
  list: (resolved?: boolean) =>
    apiClient.get<Alert[]>('/alerts', { params: { resolved } }).then((r) => r.data),

  resolve: (id: number) =>
    apiClient.patch(`/alerts/${id}/resolve`),
}
