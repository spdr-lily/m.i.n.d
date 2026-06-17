import apiClient from './client'
import type { User, RolePermission, RoutePermission, MonitoringStats, HealthStatus, RequestLog } from '../types'

export const adminApi = {
  listUsers: (page = 1, size = 20) =>
    apiClient.get<{ total: number; users: User[] }>('/admin/users', { params: { page, size } }).then((r) => r.data),

  getUser: (uuid: string) =>
    apiClient.get<User>(`/admin/users/${uuid}`).then((r) => r.data),

  updateUser: (uuid: string, data: Partial<User>) =>
    apiClient.patch<User>(`/admin/users/${uuid}`, data).then((r) => r.data),

  deleteUser: (uuid: string) =>
    apiClient.delete(`/admin/users/${uuid}`),

  createUser: (data: { username: string; password: string; full_name?: string; role?: string }) =>
    apiClient.post<User>('/admin/users', data).then((r) => r.data),

  changePassword: (uuid: string, new_password: string) =>
    apiClient.patch(`/admin/users/${uuid}/password`, { new_password }),

  // Permissions
  listPermissions: () =>
    apiClient.get<{ total: number; permissions: RolePermission[] }>('/admin/permissions').then((r) => r.data),

  addPermission: (data: RolePermission) =>
    apiClient.post<RolePermission>('/admin/permissions', data).then((r) => r.data),

  removePermission: (id: number) =>
    apiClient.delete(`/admin/permissions/${id}`),

  // Route Permissions
  listRoutePermissions: () =>
    apiClient.get<{ total: number; routes: RoutePermission[] }>('/admin/route-permissions').then((r) => r.data),

  addRoutePermission: (data: RoutePermission) =>
    apiClient.post<RoutePermission>('/admin/route-permissions', data).then((r) => r.data),

  updateRoutePermission: (id: number, data: Partial<RoutePermission>) =>
    apiClient.patch<RoutePermission>(`/admin/route-permissions/${id}`, data).then((r) => r.data),

  deleteRoutePermission: (id: number) =>
    apiClient.delete(`/admin/route-permissions/${id}`),

  // Monitoring
  stats: () =>
    apiClient.get<MonitoringStats>('/admin/monitoring/stats').then((r) => r.data),

  health: () =>
    apiClient.get<HealthStatus>('/admin/monitoring/health').then((r) => r.data),

  requests: () =>
    apiClient.get<{ requests: RequestLog[] }>('/admin/monitoring/requests').then((r) => r.data),
}
