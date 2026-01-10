import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE || '/api/v1'
const msBase = import.meta.env.VITE_MS_NOTIFICATION_BASE || '/ms/notification'

export const core = axios.create({ baseURL: apiBase })
export const notification = axios.create({ baseURL: msBase })

function attachAuth(instance, getTokens, setTokens, logout) {
  instance.interceptors.request.use((config) => {
    const { access } = getTokens()
    if (access) config.headers.Authorization = `Bearer ${access}`
    config.headers['X-Request-Id'] = crypto.randomUUID()
    return config
  })

  instance.interceptors.response.use(
    (res) => res,
    async (err) => {
      const status = err?.response?.status
      const original = err.config
      if (status === 401 && !original._retry) {
        original._retry = true
        const { refresh } = getTokens()
        if (!refresh) { logout(); return Promise.reject(err) }
        try {
          const r = await core.post('/auth/refresh/', { refresh })
          const access = r.data?.data?.access
          const newRefresh = r.data?.data?.refresh || refresh
          setTokens({ access, refresh: newRefresh })
          original.headers.Authorization = `Bearer ${access}`
          return instance(original)
        } catch (e) {
          logout()
          return Promise.reject(e)
        }
      }
      return Promise.reject(err)
    }
  )
}

export function setupInterceptors({ getTokens, setTokens, logout }) {
  attachAuth(core, getTokens, setTokens, logout)
  attachAuth(notification, getTokens, setTokens, logout)
}
