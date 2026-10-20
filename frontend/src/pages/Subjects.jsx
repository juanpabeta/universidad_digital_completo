import { useState } from 'react'
import { useAuth, hasRole } from '../auth/AuthContext.jsx'
import { request } from '../api/client.js'
import { useResource } from '../hooks/useResource.js'
import { Badge, DataState, Field, Notice, PageHeader, Panel } from '../components/UI.jsx'

const blank = { nombre: '', codigo: '', creditos: 3, id_docente: '', activa: true }

export default function Subjects() {
  const { token, user } = useAuth()
  const admin = hasRole(user, 'ADMINISTRADOR')
  const subjects = useResource('/api/v1/subjects?limit=100', token)
  const users = useResource(admin ? '/api/v1/users?limit=100' : null, token)
  const teachers = (users.data || []).filter((item) => item.activo && item.roles.includes('DOCENTE'))
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  function select(item) {
    setEditing(item.id_materia)
    setForm({ nombre: item.nombre, codigo: item.codigo, creditos: item.creditos, id_docente: item.id_docente ?? '', activa: item.activa })
    setError(''); setSuccess('')
  }
  function reset() { setEditing(null); setForm(blank) }

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setSuccess('')
    const body = { nombre: form.nombre.trim(), codigo: form.codigo.trim(), creditos: Number(form.creditos), id_docente: form.id_docente ? Number(form.id_docente) : null }
    try {
      await request(editing ? `/api/v1/subjects/${editing}` : '/api/v1/subjects', { token, method: editing ? 'PUT' : 'POST', body: editing ? { ...body, activa: form.activa } : body })
      subjects.reload(); reset(); setSuccess('Materia guardada correctamente.')
    } catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  async function deactivate(item) {
    if (!window.confirm(`¿Desactivar ${item.nombre}?`)) return
    setError(''); setSuccess('')
    try { await request(`/api/v1/subjects/${item.id_materia}`, { token, method: 'DELETE' }); subjects.reload(); setSuccess('Materia desactivada.') }
    catch (cause) { setError(cause.message) }
  }

  return <><PageHeader eyebrow="OFERTA ACADÉMICA" title="Materias" description="Consulte la oferta y sus docentes responsables." /><Notice type="error">{error}</Notice><Notice type="success">{success}</Notice><div className={admin ? 'content-grid' : ''}><Panel title="Catálogo de materias" subtitle="Código, créditos y estado"><DataState resource={subjects} emptyMessage="Aún no hay materias.">{(items) => <div className="table-wrap"><table><thead><tr><th>Materia</th><th>Créditos</th><th>Docente</th><th>Estado</th>{admin && <th>Acciones</th>}</tr></thead><tbody>{items.map((item) => <tr key={item.id_materia}><td><strong>{item.nombre}</strong><small>{item.codigo}</small></td><td>{item.creditos}</td><td>{users.data?.find((entry) => entry.id_usuario === item.id_docente)?.nombres || (item.id_docente ? `#${item.id_docente}` : 'Sin asignar')}</td><td><Badge tone={item.activa ? 'success' : 'neutral'}>{item.activa ? 'Activa' : 'Inactiva'}</Badge></td>{admin && <td className="actions"><button type="button" className="inline-button" onClick={() => select(item)}>Editar</button>{item.activa && <button type="button" className="inline-button danger" onClick={() => deactivate(item)}>Desactivar</button>}</td>}</tr>)}</tbody></table></div>}</DataState></Panel>
      {admin && <Panel title={editing ? 'Editar materia' : 'Nueva materia'} subtitle="Asigne un docente activo para que pueda registrar notas"><form onSubmit={submit} className="stack-form"><Field label="Nombre"><input required minLength="2" maxLength="150" value={form.nombre} onChange={(event) => setForm({ ...form, nombre: event.target.value })} /></Field><div className="form-pair"><Field label="Código"><input required minLength="2" maxLength="30" value={form.codigo} onChange={(event) => setForm({ ...form, codigo: event.target.value })} /></Field><Field label="Créditos"><input required type="number" min="1" max="30" value={form.creditos} onChange={(event) => setForm({ ...form, creditos: event.target.value })} /></Field></div><Field label="Docente responsable"><select value={form.id_docente} onChange={(event) => setForm({ ...form, id_docente: event.target.value })}><option value="">Sin asignar</option>{teachers.map((teacher) => <option value={teacher.id_usuario} key={teacher.id_usuario}>{teacher.nombres} {teacher.apellidos}</option>)}</select></Field>{editing && <label className="check-row"><input type="checkbox" checked={form.activa} onChange={(event) => setForm({ ...form, activa: event.target.checked })} />Materia activa</label>}<div className="form-buttons"><button className="button button-primary" disabled={busy}>{busy ? 'Guardando…' : editing ? 'Guardar cambios' : 'Crear materia'}</button>{editing && <button type="button" className="button button-quiet" onClick={reset}>Cancelar</button>}</div></form></Panel>}</div></>
}
