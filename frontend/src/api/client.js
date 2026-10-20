const configuredBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/$/, '')

export function apiOrigin() {
  if (!configuredBase) {
    throw new Error('Falta VITE_API_BASE_URL. Configure la URL pública del backend y vuelva a compilar.')
  }
  const url = new URL(configuredBase)
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.pathname !== '/' || url.search || url.hash) {
    throw new Error('VITE_API_BASE_URL debe ser un origen HTTP(S) sin ruta, consulta ni credenciales.')
  }
  if (import.meta.env.PROD && url.protocol !== 'https:') {
    throw new Error('La URL de la API para producción debe usar HTTPS.')
  }
  return url.origin
}

export class ApiError extends Error {
  constructor(message, status = 0, code = 'network_error') {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export async function request(path, { token, method = 'GET', body, signal } = {}) {
  const headers = { Accept: 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  let response
  try {
    response = await fetch(`${apiOrigin()}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new ApiError('No se pudo conectar con la API. Revise la URL, red y CORS.')
  }
  if (response.status === 204) return null
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401 && token) window.dispatchEvent(new Event('ud:session-expired'))
    const message = payload?.error?.message
      || (Array.isArray(payload?.detail) ? payload.detail.map((item) => item.msg).join('; ') : payload?.detail)
      || `La solicitud falló (${response.status}).`
    throw new ApiError(String(message), response.status, payload?.error?.code)
  }
  return payload
}

export async function login(email, password) {
  const form = new URLSearchParams({ username: email, password })
  let response
  try {
    response = await fetch(`${apiOrigin()}/api/v1/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    })
  } catch {
    throw new ApiError('No se pudo conectar con la API. Revise red, URL y CORS.')
  }
  const payload = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(payload?.error?.message || 'No fue posible iniciar sesión.', response.status)
  return payload.access_token
}
