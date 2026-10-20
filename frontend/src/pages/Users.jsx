import { useState } from 'react'
import { useAuth } from '../auth/AuthContext.jsx'
import { request } from '../api/client.js'
import { useResource } from '../hooks/useResource.js'
import { Badge, DataState, Field, Notice, PageHeader, Panel } from '../components/UI.jsx'

const roles = ['ADMINISTRADOR', 'DOCENTE', 'ESTUDIANTE']
const empty = { nombres: '', apellidos: '', email: '', password: '', roles: ['ESTUDIANTE'] }

function RoleEditor({ item, currentId, onSave }) {
  const [selected, setSelected] = useState(item.roles)
  const ownAccount = item.id_usuario === currentId
  return <details className="role-editor"><summary>{item.roles.join(', ')} ▾</summary><div className="role-popover">
    {roles.map((role) => <label key={role}><input type="checkbox" checked={selected.includes(role)} disabled={ownAccount} onChange={(event) => setSelected((previous) => event.target.checked ? [...previous, role] : previous.filter((value) => value !== role))} />{role}</label>)}
    <button type="button" className="button button-small button-primary" disabled={ownAccount || !selected.length} onClick={() => onSave(item, selected)}>Guardar roles</button>
    {ownAccount && <small>Edite su propia cuenta mediante un procedimiento supervisado.</small>}
  </div></details>
}

export default function Users() {
  const { token, user: current } = useAuth()
  const users = useResource('/api/v1/users?limit=100', token)
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  async function create(event) {
    event.preventDefault(); setBusy(true); setError(''); setSuccess('')
    try {
      await request('/api/v1/users', { token, method: 'POST', body: form })
      setForm(empty); users.reload(); setSuccess('La cuenta fue creada correctamente.')
    } catch (cause) { setError(cause.message) }
    finally { setBusy(false) }
  }

  async function toggle(user) {
    if (user.id_usuario === current.id_usuario) return
    setError(''); setSuccess('')
    try {
      await request(`/api/v1/users/${user.id_usuario}/status`, { token, method: 'PATCH', body: { activo: !user.activo } })
      users.reload(); setSuccess('Estado de la cuenta actualizado.')
    } catch (cause) { setError(cause.message) }
  }

  async function changeRoles(user, selected) {
    setError(''); setSuccess('')
    try {
      await request(`/api/v1/users/${user.id_usuario}/roles`, { token, method: 'PUT', body: { roles: selected } })
      users.reload(); setSuccess('Roles actualizados.')
    } catch (cause) { setError(cause.message) }
  }

  return <><PageHeader eyebrow="ADMINISTRACIÓN" title="Usuarios" description="Cree cuentas y administre el acceso al sistema académico." /><Notice type="error">{error}</Notice><Notice type="success">{success}</Notice><div className="content-grid"><Panel title="Directorio" subtitle="Primeros 100 usuarios, ordenados por identificador"><DataState resource={users} emptyMessage="No hay usuarios disponibles.">{(items) => <div className="table-wrap"><table><thead><tr><th>Usuario</th><th>Roles</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{items.map((item) => <tr key={item.id_usuario}><td><strong>{item.nombres} {item.apellidos}</strong><small>{item.email}</small></td><td><RoleEditor key={`${item.id_usuario}-${item.roles.join('-')}`} item={item} currentId={current.id_usuario} onSave={changeRoles} /></td><td><Badge tone={item.activo ? 'success' : 'neutral'}>{item.activo ? 'Activo' : 'Inactivo'}</Badge></td><td><button className="button button-small button-quiet" disabled={item.id_usuario === current.id_usuario} onClick={() => toggle(item)}>{item.activo ? 'Desactivar' : 'Activar'}</button></td></tr>)}</tbody></table></div>}</DataState></Panel>
      <Panel title="Nueva cuenta" subtitle="La contraseña se transmite a la API por HTTPS; nunca se muestra en el listado"><form onSubmit={create} className="stack-form"><div className="form-pair"><Field label="Nombres"><input required maxLength="100" value={form.nombres} onChange={(event) => setForm({ ...form, nombres: event.target.value })} /></Field><Field label="Apellidos"><input required maxLength="100" value={form.apellidos} onChange={(event) => setForm({ ...form, apellidos: event.target.value })} /></Field></div><Field label="Correo"><input required type="email" maxLength="254" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></Field><Field label="Contraseña inicial" hint="Al menos 12 caracteres; compártala por un canal apropiado."><input required type="password" minLength="12" maxLength="128" autoComplete="new-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></Field><fieldset className="role-fieldset"><legend>Roles</legend>{roles.map((role) => <label key={role}><input type="checkbox" checked={form.roles.includes(role)} onChange={(event) => setForm({ ...form, roles: event.target.checked ? [...form.roles, role] : form.roles.filter((value) => value !== role) })} />{role}</label>)}</fieldset><button className="button button-primary" disabled={busy || !form.roles.length}>{busy ? 'Guardando…' : 'Crear usuario'}</button></form></Panel></div></>
}
