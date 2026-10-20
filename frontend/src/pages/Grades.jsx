import { useState } from 'react'
import { useAuth, hasRole } from '../auth/AuthContext.jsx'
import { request } from '../api/client.js'
import { useResource } from '../hooks/useResource.js'
import { Badge, DataState, Field, Notice, PageHeader, Panel } from '../components/UI.jsx'

const blank = { id_inscripcion: '', nota: '', tipo: 'PARCIAL' }

export default function Grades() {
  const { token, user } = useAuth()
  const admin = hasRole(user, 'ADMINISTRADOR')
  const canWrite = admin || hasRole(user, 'DOCENTE')
  const grades = useResource('/api/v1/grades?limit=100', token)
  const enrollments = useResource('/api/v1/enrollments?limit=100', token)
  const subjects = useResource('/api/v1/subjects?limit=100', token)
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  function enrollmentLabel(id) {
    const enrollment = enrollments.data?.find((entry) => entry.id_inscripcion === id)
    if (!enrollment) return `Inscripción #${id}`
    const subject = subjects.data?.find((entry) => entry.id_materia === enrollment.id_materia)
    return `${subject?.nombre || `Materia #${enrollment.id_materia}`} · estudiante #${enrollment.id_usuario}`
  }
  async function submit(event) {
    event.preventDefault(); setError(''); setSuccess('')
    const value = Number(form.nota)
    if (form.nota === '' || !Number.isFinite(value) || value < 0 || value > 100) { setError('La nota debe estar entre 0 y 100.'); return }
    setBusy(true)
    try {
      const body = { nota: value, tipo: form.tipo }
      if (!editing) body.id_inscripcion = Number(form.id_inscripcion)
      await request(editing ? `/api/v1/grades/${editing}` : '/api/v1/grades', { token, method: editing ? 'PUT' : 'POST', body })
      grades.reload(); setForm(blank); setEditing(null); setSuccess('Calificación guardada.')
    } catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  async function remove(item) {
    if (!window.confirm('¿Eliminar esta calificación? Esta acción no se puede deshacer desde la interfaz.')) return
    setError(''); setSuccess('')
    try { await request(`/api/v1/grades/${item.id_calificacion}`, { token, method: 'DELETE' }); grades.reload(); setSuccess('Calificación eliminada.') }
    catch (cause) { setError(cause.message) }
  }

  const assignable = (enrollments.data || []).filter((item) => item.estado === 'ACTIVA')
  return <><PageHeader eyebrow="SEGUIMIENTO ACADÉMICO" title="Calificaciones" description="Registre y consulte resultados según su función académica." /><Notice type="error">{error}</Notice><Notice type="success">{success}</Notice><div className={canWrite ? 'content-grid' : ''}><Panel title="Notas registradas" subtitle="Valores de 0 a 100, con permisos definidos por el backend"><DataState resource={grades} emptyMessage="Aún no hay calificaciones visibles.">{(items) => <div className="table-wrap"><table><thead><tr><th>Inscripción</th><th>Tipo</th><th>Nota</th>{canWrite && <th>Acciones</th>}</tr></thead><tbody>{items.map((item) => <tr key={item.id_calificacion}><td><strong>{enrollmentLabel(item.id_inscripcion)}</strong><small>Calificación #{item.id_calificacion}</small></td><td><Badge tone="blue">{item.tipo}</Badge></td><td><strong className="grade-value">{Number(item.nota).toFixed(2)}</strong></td>{canWrite && <td className="actions"><button className="inline-button" type="button" onClick={() => { setEditing(item.id_calificacion); setForm({ id_inscripcion: String(item.id_inscripcion), nota: String(item.nota), tipo: item.tipo }); setError('') }}>Editar</button>{admin && <button className="inline-button danger" type="button" onClick={() => remove(item)}>Eliminar</button>}</td>}</tr>)}</tbody></table></div>}</DataState></Panel>{canWrite && <Panel title={editing ? 'Editar calificación' : 'Nueva calificación'} subtitle="Solo se admiten inscripciones activas"><form onSubmit={submit} className="stack-form"><Field label="Inscripción"><select required disabled={Boolean(editing)} value={form.id_inscripcion} onChange={(event) => setForm({ ...form, id_inscripcion: event.target.value })}><option value="">Seleccione inscripción</option>{assignable.map((item) => <option key={item.id_inscripcion} value={item.id_inscripcion}>{enrollmentLabel(item.id_inscripcion)}</option>)}</select></Field><Field label="Tipo de evaluación"><select value={form.tipo} onChange={(event) => setForm({ ...form, tipo: event.target.value })}><option>PARCIAL</option><option>FINAL</option><option>RECUPERACION</option></select></Field><Field label="Nota"><input type="number" required min="0" max="100" step="0.01" value={form.nota} onChange={(event) => setForm({ ...form, nota: event.target.value })} /></Field><div className="form-buttons"><button className="button button-primary" disabled={busy}>{busy ? 'Guardando…' : editing ? 'Guardar cambios' : 'Registrar nota'}</button>{editing && <button type="button" className="button button-quiet" onClick={() => { setEditing(null); setForm(blank) }}>Cancelar</button>}</div></form></Panel>}</div></>
}
