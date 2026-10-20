import { useCallback, useEffect, useState } from 'react'
import { request } from '../api/client.js'

export function useResource(path, token) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(Boolean(path))
  const [error, setError] = useState('')
  const [version, setVersion] = useState(0)
  const reload = useCallback(() => setVersion((value) => value + 1), [])

  useEffect(() => {
    if (!path || !token) {
      setData(null)
      setLoading(false)
      return
    }
    const controller = new AbortController()
    setLoading(true)
    setError('')
    request(path, { token, signal: controller.signal })
      .then(setData)
      .catch((cause) => {
        if (cause.name !== 'AbortError') setError(cause.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [path, token, version])

  return { data, loading, error, reload }
}
