import { createContext, useContext, useEffect, useState } from 'react'
import { login as apiLogin, request } from '../api/client.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('idle')

  useEffect(() => {
    const expire = () => {
      setToken(null)
      setUser(null)
      setStatus('expired')
    }
    window.addEventListener('ud:session-expired', expire)
    return () => window.removeEventListener('ud:session-expired', expire)
  }, [])

  async function signIn(email, password) {
    const newToken = await apiLogin(email, password)
    const profile = await request('/api/v1/users/me', { token: newToken })
    setToken(newToken)
    setUser(profile)
    setStatus('idle')
  }

  function signOut() {
    setToken(null)
    setUser(null)
    setStatus('idle')
  }

  return <AuthContext.Provider value={{ token, user, status, signIn, signOut }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('AuthProvider no está disponible')
  return context
}

export function hasRole(user, role) {
  return Boolean(user?.roles?.includes(role))
}
