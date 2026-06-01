import apiClient from './client'
import type { PaginatedAuditLogs } from '../types'

export const auditApi = {
  list: (page = 1, size = 20, entity?: string, operation?: string) =>
    apiClient
      .get<PaginatedAuditLogs>('/audit/logs', { params: { page, size, entity_name: entity, operation_type: operation } })
      .then((r) => r.data),
}
