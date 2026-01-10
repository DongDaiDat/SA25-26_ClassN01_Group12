import React, { useEffect, useState } from 'react'
import { notification } from '../api/client.js'

export default function Notifications() {
  const [items, setItems] = useState([])
  const [err, setErr] = useState(null)

  const load = () => notification.get('/messages/').then(r=>setItems(r.data||[])).catch(()=>setErr('Failed to load'))
  useEffect(()=>{ load() }, [])

  return (
    <div className="card">
      <h2>Notification History</h2>
      {err && <p className="error">{err}</p>}
      <table className="table">
        <thead><tr><th>Time</th><th>Type</th><th>To</th><th>Subject</th><th>Status</th></tr></thead>
        <tbody>
          {items.map(m => (
            <tr key={m.id}>
              <td>{new Date(m.created_at).toLocaleString()}</td>
              <td>{m.event_type}</td>
              <td>{m.to}</td>
              <td>{m.subject}</td>
              <td>{m.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{fontSize:12, opacity:0.8}}>Note: Notification API currently has no auth for simplicity (GIẢ ĐỊNH dev). Add auth for production.</p>
    </div>
  )
}
