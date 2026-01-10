import React, { useEffect, useState } from 'react'
import { useAuth } from '../state/auth.jsx'

export default function Dashboard() {
  const { me } = useAuth()
  const [health, setHealth] = useState({ status: '...' })

  useEffect(() => {
    let alive = true

    ;(async () => {
      try {
        const res = await fetch('/api/health', { method: 'GET' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        if (alive) setHealth(json?.data || { status: 'down' })
      } catch (e) {
        if (alive) setHealth({ status: 'down' })
      }
    })()

    return () => {
      alive = false
    }
  }, [])

  return (
    <div className="card">
      <h2>Dashboard</h2>

      <p>
        Core health: <b>{health?.status || '...'}</b>
      </p>

      {me?.role === 'STUDENT' && <p>Tip: Go to Enrollment to register sections.</p>}
      {me?.role === 'INSTRUCTOR' && <p>Tip: Go to Grade Entry to enter and publish grades.</p>}
      {me?.role === 'ADMIN' && <p>Tip: Use Program/Course Catalog/Term to manage the training structure.</p>}
    </div>
  )
}
