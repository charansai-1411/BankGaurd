import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { session, initialized, initialize } = useAuthStore()

  useEffect(() => {
    if (!initialized) {
      initialize()
    }
  }, [initialized, initialize])

  if (!initialized) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center font-mono text-gold text-[10px] tracking-widest uppercase">
        INITIALIZING SECURE SESSION...
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
