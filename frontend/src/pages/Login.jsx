import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { Field, Notice } from '../components/UI.jsx'

export default function Login() {
  const { user, status, signIn } = useAuth()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  if (user) return <Navigate to={location.state?.from || '/'} replace />

  async function submit(event) {
    event.preventDefault()
    setBusy(true); setError('')
    try { await signIn(email.trim(), password) }
    catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  return <div className="login-page">
    <div className="login-intro"><div className="login-brand"><span>U</span> UNIVERSIDAD DIGITAL</div><div className="login-story"><p className="eyebrow">CAMPUS · GESTIÓN INTEGRADA</p><h1>Un espacio para<br /><em>aprender, gestionar<br />y avanzar.</em></h1><p>Una sola experiencia para organizar la vida académica de estudiantes, docentes y administración.</p><div className="login-lines"><span>01 / Usuarios y roles</span><span>02 / Trayectoria académica</span><span>03 / Información confiable</span></div></div><div className="login-foot">Plataforma académica · Universidad Digital</div></div>
    <div className="login-form-side"><div className="login-card"><div className="login-mark">U</div><p className="eyebrow">BIENVENIDO DE NUEVO</p><h2>Iniciar sesión</h2><p className="muted">Ingrese con la cuenta creada por administración para acceder a su espacio académico.</p>{status === 'expired' && <Notice type="error">Su sesión expiró. Inicie sesión de nuevo.</Notice>}<Notice type="error">{error}</Notice><form onSubmit={submit} className="stack-form"><Field label="Correo institucional"><input type="email" required autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="nombre@universidad.edu.co" /></Field><Field label="Contraseña"><input type="password" required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Su contraseña" /></Field><button className="button button-primary button-wide" disabled={busy}>{busy ? 'Verificando…' : 'Ingresar al campus'} <span aria-hidden="true">↗</span></button></form><p className="login-help">Las cuentas las administra la institución. Solicite apoyo al administrador si no puede ingresar.</p></div></div>
  </div>
}
