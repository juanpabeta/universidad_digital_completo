import { useState } from 'react'
import { useAuth, hasRole } from '../auth/AuthContext.jsx'
import { request } from '../api/client.js'
import { useResource } from '../hooks/useResource.js'
import { Badge, DataState, Field, Notice, PageHeader, Panel } from '../components/UI.jsx'

export default function Enrollments() {
  const { token, user } = useAuth()
  const admin = hasRole(user, 'ADMINISTRADOR')
  const student = hasRole(user, 'ESTUDIANTE')
  const enrollments = useResource('/api/v1/enrollments?limit=100', token)
  const subjects = useResource('/api/v1/subjects?limit=100', token)
  const periods = useResource('/api/v1/periods?limit=100', token)
  const users = useResource(admin ? '/api/v1/users?limit=100' : null, token)
  const [form, setForm] = useState({ id_usuario: '', id_materia: '', id_periodo: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault(); setError(''); setSuccess(''); setBusy(true)
    const body = { id_materia: Number(form.id_materia), id_periodo: Number(form.id_periodo) }
    if (admin) body.id_usuario = Number(form.id_usuario)
    try {
      await request('/api/v1/enrollments', { token, method: 'POST', body })
      enrollments.reload(); setForm({ id_usuario: '', id_materia: '', id_periodo: '' }); setSuccess('Inscripción registrada.')
    } catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  async function cancel(item) {
    if (!window.confirm('¿Cancelar esta inscripción?')) return
    setError(''); setSuccess('')
    try { await request(`/api/v1/enrollments/${item.id_inscripcion}`, { token, method: 'DELETE' }); enrollments.reload(); setSuccess('Inscripción cancelada.') }
    catch (cause) { setError(cause.message) }
  }

  const canEnroll = admin || student
  const available = (periods.data || []).filter((period) => period.estado === 'ABIERTO')
  return <><PageHeader eyebrow="TRAYECTORIA ACADÉMICA" title="Inscripciones" description="Consulte y gestione la matrícula en materias y períodos vigentes." /><Notice type="error">{error}</Notice><Notice type="success">{success}</Notice><div className={canEnroll ? 'content-grid' : ''}><Panel title="Registro de inscripciones" subtitle="La API muestra únicamente los registros permitidos para su cuenta"><DataState resource={enrollments} emptyMessage="Aún no hay inscripciones visibles.">{(items) => <div className="table-wrap"><table><thead><tr><th>Materia</th><th>Período</th><th>Estudiante</th><th>Estado</th>{canEnroll && <th>Acción</th>}</tr></thead><tbody>{items.map((item) => <tr key={item.id_inscripcion}><td><strong>{subjects.data?.find((s) => s.id_materia === item.id_materia)?.nombre || `Materia #${item.id_materia}`}</strong><small>Inscripción #{item.id_inscripcion}</small></td><td>{periods.data?.find((p) => p.id_periodo === item.id_periodo)?.nombre || `#${item.id_periodo}`}</td><td>{admin ? (users.data?.find((entry) => entry.id_usuario === item.id_usuario)?.nombres || `#${item.id_usuario}`) : item.id_usuario === user.id_usuario ? 'Yo' : `#${item.id_usuario}`}</td><td><Badge tone={item.estado === 'ACTIVA' ? 'success' : 'neutral'}>{item.estado}</Badge></td>{canEnroll && <td>{item.estado === 'ACTIVA' && (admin || item.id_usuario === user.id_usuario) && <button type="button" className="inline-button danger" onClick={() => cancel(item)}>Cancelar</button>}</td>}</tr>)}</tbody></table></div>}</DataState></Panel>{canEnroll && <Panel title="Nueva inscripción" subtitle="El período debe estar abierto y dentro de sus fechas"><form onSubmit={submit} className="stack-form">{admin && <Field label="Estudiante"><select required value={form.id_usuario} onChange={(event) => setForm({ ...form, id_usuario: event.target.value })}><option value="">Seleccione estudiante</option>{(users.data || []).filter((entry) => entry.activo && entry.roles.includes('ESTUDIANTE')).map((entry) => <option key={entry.id_usuario} value={entry.id_usuario}>{entry.nombres} {entry.apellidos}</option>)}</select></Field>}<Field label="Materia"><select required value={form.id_materia} onChange={(event) => setForm({ ...form, id_materia: event.target.value })}><option value="">Seleccione materia</option>{(subjects.data || []).filter((item) => item.activa).map((item) => <option key={item.id_materia} value={item.id_materia}>{item.nombre} · {item.codigo}</option>)}</select></Field><Field label="Período"><select required value={form.id_periodo} onChange={(event) => setForm({ ...form, id_periodo: event.target.value })}><option value="">Seleccione período</option>{available.map((item) => <option key={item.id_periodo} value={item.id_periodo}>{item.nombre}</option>)}</select></Field><button className="button button-primary" disabled={busy}>{busy ? 'Registrando…' : 'Registrar inscripción'}</button></form></Panel>}</div></>
}
