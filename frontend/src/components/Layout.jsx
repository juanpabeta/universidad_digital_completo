import { NavLink, useNavigate } from 'react-router-dom'
import { hasRole, useAuth } from '../auth/AuthContext.jsx'

const links = [
  { to: '/', label: 'Resumen', symbol: '▦' },
  { to: '/users', label: 'Usuarios', symbol: '◎', roles: ['ADMINISTRADOR'] },
  { to: '/subjects', label: 'Materias', symbol: '▤' },
  { to: '/periods', label: 'Períodos', symbol: '◷' },
  { to: '/enrollments', label: 'Inscripciones', symbol: '◫' },
  { to: '/grades', label: 'Calificaciones', symbol: '◆' },
  { to: '/reports', label: 'Reportes', symbol: '▥', roles: ['ADMINISTRADOR', 'DOCENTE'] },
]

export default function Layout({ children }) {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  function leave() { signOut(); navigate('/') }
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-icon" aria-hidden="true">U</div><div><strong>Universidad<br />Digital</strong><small>Gestión académica</small></div></div>
      <p className="sidebar-label">ESPACIO DE TRABAJO</p>
      <nav className="main-nav" aria-label="Navegación principal">
        {links.filter((link) => !link.roles || link.roles.some((role) => hasRole(user, role))).map((link) =>
          <NavLink key={link.to} to={link.to} end={link.to === '/'} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-symbol" aria-hidden="true">{link.symbol}</span>{link.label}
          </NavLink>)}
      </nav>
      <div className="sidebar-footer"><span className="signal-dot" /> Sistema académico <small>Frontend React · API FastAPI</small></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb">Universidad Digital <span>/</span> Campus</div><div className="account"><div className="avatar" aria-hidden="true">{user.nombres?.[0]}{user.apellidos?.[0]}</div><div className="account-name"><strong>{user.nombres} {user.apellidos}</strong><small>{user.roles?.join(' · ')}</small></div><button type="button" className="button button-quiet" onClick={leave}>Salir</button></div></header>
      <main className="main-content">{children}</main>
      <footer className="site-footer">Universidad Digital · Entorno académico de demostración</footer>
    </div>
  </div>
}
