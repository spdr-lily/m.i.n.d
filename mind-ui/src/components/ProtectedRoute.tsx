import { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuthStore } from '../store/authStore'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, token, loading, loadUser } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    if (token && !user) loadUser()
  }, [token, user, loadUser])

  if (!token) return <Navigate to="/login" state={{ from: location }} replace />
  if (loading) return <Spin style={{ display: 'block', margin: '200px auto' }} size="large" />
  if (!user) return null

  return <>{children}</>
}
