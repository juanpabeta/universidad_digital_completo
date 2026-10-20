export function PageHeader({ eyebrow, title, description, children }) {
  return <div className="page-header">
    <div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lead">{description}</p></div>
    {children && <div className="header-action">{children}</div>}
  </div>
}

export function Panel({ title, subtitle, children, className = '' }) {
  return <section className={`panel ${className}`}>
    {(title || subtitle) && <div className="panel-heading"><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>}
    {children}
  </section>
}

export function Notice({ type = 'info', children }) {
  if (!children) return null
  return <div role={type === 'error' ? 'alert' : 'status'} className={`notice notice-${type}`}>{children}</div>
}

export function Empty({ children = 'Todavía no hay registros para mostrar.' }) {
  return <div className="empty-state"><span className="empty-mark">◇</span><p>{children}</p></div>
}

export function DataState({ resource, children, emptyMessage }) {
  if (resource.loading && !resource.data) return <p className="muted" role="status">Cargando información…</p>
  if (resource.error) return <Notice type="error">{resource.error} <button className="inline-button" type="button" onClick={resource.reload}>Reintentar</button></Notice>
  if (!resource.data?.length) return <Empty>{emptyMessage}</Empty>
  return children(resource.data)
}

export function Field({ label, children, hint }) {
  return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>
}

export function Badge({ children, tone = 'neutral' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

export function formatDate(value) {
  if (!value) return '—'
  const date = String(value).slice(0, 10)
  return /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : String(value)
}

export function nameOf(items, id, key, fallback = `#${id}`) {
  return items?.find((item) => item[key] === id)?.nombre || fallback
}
