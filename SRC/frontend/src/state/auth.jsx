import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { setupInterceptors, core } from '../api/client.js'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(() => {
    const raw = localStorage.getItem('tpms_tokens')
    return raw ? JSON.parse(raw) : { access: null, refresh: null }
  })
  const [me, setMe] = useState(() => {
    const raw = localStorage.getItem('tpms_me')
    return raw ? JSON.parse(raw) : null
  })

  useEffect(() => {
    localStorage.setItem('tpms_tokens', JSON.stringify(tokens))
  }, [tokens])
  useEffect(() => {
    localStorage.setItem('tpms_me', JSON.stringify(me))
  }, [me])

  const api = useMemo(() => ({
    getTokens: () => tokens,
    setTokens: (t) => setTokens(t),
    logout: () => { setTokens({ access: null, refresh: null }); setMe(null); }
  }), [tokens])

  useEffect(() => {
    setupInterceptors(api)
  }, [api])

  const login = async (username, password) => {
    const r = await core.post('/auth/login/', { username, password })
    const access = r.data?.data?.access
    const refresh = r.data?.data?.refresh
    setTokens({ access, refresh })
    // fetch me using admin endpoint? we don't have /me. We'll decode role by calling /auth/users? not allowed.
    // We'll call /auth/users/{id} isn't available. Simplest: ask backend to include role in token? Not.
    // Assumption: use /api/v1/auth/login returns tokens only. We'll add /api/v1/auth/whoami endpoint in backend.
    const meRes = await core.get('/auth/whoami/')
    setMe(meRes.data?.data)
  }

  const value = { tokens, me, login, logout: api.logout, setMe }
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}

export function useAuth() { return useContext(AuthCtx) }
