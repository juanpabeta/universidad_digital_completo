import { useState } from 'react'
import { useAuth, hasRole } from '../auth/AuthContext.jsx'
import { request } from '../api/client.js'
import { useResource } from '../hooks/useResource.js'
import { Badge, DataState, Field, Notice, PageHeader, Panel, formatDate } from '../components/UI.jsx'

const blank = { nombre: '', fecha_inicio: '', fecha_fin: '', estado: 'ABIERTO' }

export default function Periods() {
  const { token, user } = useAuth()
  const admin = hasRole(user, 'ADMINISTRADOR')
  const periods = useResource('/api/v1/periods?limit=100', token)
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault(); setError(''); setSuccess('')
    if (form.fecha_fin < form.fecha_inicio) { setError('La fecha final debe ser igual o posterior a la fecha inicial.'); return }
    setBusy(true)
    try {
      await request(editing ? `/api/v1/periods/${editing}` : '/api/v1/periods', { token, method: editing ? 'PUT' : 'POST', body: form })
      periods.reload(); setEditing(null); setForm(blank); setSuccess('Período guardado.')
    } catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  return <><PageHeader eyebrow="CALENDARIO ACADÉMICO" title="Períodos" description="Fechas y disponibilidad para las inscripciones." /><Notice type="error">{error}</Notice><Notice type="success">{success}</Notice><div className={admin ? 'content-grid' : ''}><Panel title="Períodos registrados" subtitle="La inscripción requiere un período abierto y vigente"><DataState resource={periods} emptyMessage="Aún no hay períodos académicos.">{(items) => <div className="table-wrap"><table><thead><tr><th>Período</th><th>Inicio</th><th>Fin</th><th>Estado</th>{admin && <th></th>}</tr></thead><tbody>{items.map((item) => <tr key={item.id_periodo}><td><strong>{item.nombre}</strong></td><td>{formatDate(item.fecha_inicio)}</td><td>{formatDate(item.fecha_fin)}</td><td><Badge tone={item.estado === 'ABIERTO' ? 'success' : 'neutral'}>{item.estado}</Badge></td>{admin && <td><button type="button" className="inline-button" onClick={() => { setEditing(item.id_periodo); setForm({ nombre: item.nombre, fecha_inicio: item.fecha_inicio, fecha_fin: item.fecha_fin, estado: item.estado }); setError('') }}>Editar</button></td>}</tr>)}</tbody></table></div>}</DataState></Panel>{admin && <Panel title={editing ? 'Editar período' : 'Nuevo período'} subtitle="Las fechas se validan también en el servidor"><form onSubmit={submit} className="stack-form"><Field label="Nombre"><input required minLength="2" maxLength="30" value={form.nombre} onChange={(event) => setForm({ ...form, nombre: event.target.value })} placeholder="2026-2" /></Field><Field label="Fecha de inicio"><input required type="date" value={form.fecha_inicio} onChange={(event) => setForm({ ...form, fecha_inicio: event.target.value })} /></Field><Field label="Fecha de fin"><input required type="date" min={form.fecha_inicio || undefined} value={form.fecha_fin} onChange={(event) => setForm({ ...form, fecha_fin: event.target.value })} /></Field><Field label="Estado"><select value={form.estado} onChange={(event) => setForm({ ...form, estado: event.target.value })}><option>ABIERTO</option><option>CERRADO</option></select></Field><div className="form-buttons"><button className="button button-primary" disabled={busy}>{busy ? 'Guardando…' : editing ? 'Guardar cambios' : 'Crear período'}</button>{editing && <button type="button" className="button button-quiet" onClick={() => { setEditing(null); setForm(blank) }}>Cancelar</button>}</div></form></Panel>}</div></>
}
