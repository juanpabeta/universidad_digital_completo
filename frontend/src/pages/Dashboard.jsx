import { Link } from 'react-router-dom'
import { useAuth, hasRole } from '../auth/AuthContext.jsx'
import { useResource } from '../hooks/useResource.js'
import { DataState, PageHeader, Panel, Badge, formatDate } from '../components/UI.jsx'

export default function Dashboard() {
  const { user, token } = useAuth()
  const admin = hasRole(user, 'ADMINISTRADOR')
  const users = useResource(admin ? '/api/v1/users?limit=100' : null, token)
  const subjects = useResource('/api/v1/subjects?limit=100', token)
  const periods = useResource('/api/v1/periods?limit=100', token)
  const enrollments = useResource('/api/v1/enrollments?limit=100', token)
  const metrics = [
    { label: 'Materias', value: subjects.data?.length, symbol: '▤', color: 'blue' },
    { label: 'Períodos', value: periods.data?.length, symbol: '◷', color: 'amber' },
    { label: admin ? 'Usuarios' : 'Inscripciones visibles', value: admin ? users.data?.length : enrollments.data?.length, symbol: '◎', color: 'green' },
  ]
  return <>
    <PageHeader eyebrow="PANEL GENERAL" title={`Hola, ${user.nombres}`} description="Una vista clara de la actividad académica y los próximos pasos." />
    <section className="hero-panel"><div><p className="eyebrow">UNIVERSIDAD DIGITAL</p><h2>La información que necesita,<br />en un mismo lugar.</h2><p>Gestione materias, consulte sus inscripciones y dé seguimiento al período académico actual.</p><Link className="button button-light" to={admin ? '/users' : '/enrollments'}>{admin ? 'Gestionar usuarios' : 'Ver inscripciones'} <span aria-hidden="true">↗</span></Link></div><div className="hero-art" aria-hidden="true"><span>U</span><i /><i /></div></section>
    <div className="metric-grid">{metrics.map((metric) => <div className="metric-card" key={metric.label}><div className={`metric-icon ${metric.color}`}>{metric.symbol}</div><p>{metric.label}</p><strong>{metric.value ?? '—'}</strong><small>Registros visibles</small></div>)}</div>
    <div className="two-column"><Panel title="Materias recientes" subtitle="Oferta académica visible en su cuenta"><DataState resource={subjects} emptyMessage="Aún no se han creado materias.">{(items) => <div className="list-rows">{items.slice(-5).reverse().map((item) => <div className="list-row" key={item.id_materia}><div className="list-icon">▤</div><div><strong>{item.nombre}</strong><small>{item.codigo} · {item.creditos} créditos</small></div><Badge tone={item.activa ? 'success' : 'neutral'}>{item.activa ? 'Activa' : 'Inactiva'}</Badge></div>)}</div>}</DataState><Link className="text-link" to="/subjects">Ver todas las materias →</Link></Panel>
      <Panel title="Períodos académicos" subtitle="Fechas y estado de cada período"><DataState resource={periods} emptyMessage="Aún no hay períodos.">{(items) => <div className="list-rows">{items.slice(-4).reverse().map((item) => <div className="list-row" key={item.id_periodo}><div className="list-icon amber">◷</div><div><strong>{item.nombre}</strong><small>{formatDate(item.fecha_inicio)} al {formatDate(item.fecha_fin)}</small></div><Badge tone={item.estado === 'ABIERTO' ? 'success' : 'neutral'}>{item.estado}</Badge></div>)}</div>}</DataState><Link className="text-link" to="/periods">Consultar períodos →</Link></Panel></div>
  </>
}
