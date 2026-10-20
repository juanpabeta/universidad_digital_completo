import { useState } from 'react'
import { useAuth } from '../auth/AuthContext.jsx'
import { useResource } from '../hooks/useResource.js'
import { DataState, Empty, Field, PageHeader, Panel } from '../components/UI.jsx'

export default function Reports() {
  const { token } = useAuth()
  const [periodId, setPeriodId] = useState('')
  const periods = useResource('/api/v1/periods?limit=100', token)
  const report = useResource(periodId ? `/api/v1/reports/periods/${periodId}/subjects` : null, token)
  return <><PageHeader eyebrow="ANÁLISIS ACADÉMICO" title="Reportes" description="Revise inscripciones activas y promedio de calificaciones por materia." /><Panel title="Seleccione un período" subtitle="El reporte respeta sus permisos de docente o administración"><Field label="Período académico"><select className="report-select" value={periodId} onChange={(event) => setPeriodId(event.target.value)}><option value="">Seleccione un período</option>{(periods.data || []).map((period) => <option key={period.id_periodo} value={period.id_periodo}>{period.nombre}</option>)}</select></Field>{periods.error && <p role="alert" className="error-text">{periods.error}</p>}</Panel><div className="spacer" /><Panel title="Resumen por materia" subtitle="El promedio refleja las calificaciones registradas de inscripciones activas">{!periodId ? <Empty>Seleccione un período para generar el reporte.</Empty> : <DataState resource={report} emptyMessage="No hay materias visibles para este período.">{(rows) => <div className="table-wrap"><table><thead><tr><th>Materia</th><th>Inscripciones activas</th><th>Promedio de calificaciones</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id_materia}><td><strong>{row.materia}</strong></td><td>{row.inscripciones_activas}</td><td><strong className="grade-value">{row.promedio_calificaciones == null ? 'Sin notas' : Number(row.promedio_calificaciones).toFixed(2)}</strong></td></tr>)}</tbody></table></div>}</DataState>}</Panel></>
}
