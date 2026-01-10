import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function Programs() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ code:'', name:'', status:'ACTIVE' })
  const [err, setErr] = useState(null)

  const load = () => core.get('/program/programs/').then(r=>setItems(r.data?.data||[]))
  useEffect(()=>{ load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr(null)
    try {
      await core.post('/program/programs/', form)
      setForm({ code:'', name:'', status:'ACTIVE' })
      load()
    } catch (e) { setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Programs</h2>
        {err && <p className="error">{err}</p>}
        <form onSubmit={submit} className="row">
          <div style={{flex:1}}>
            <input className="input" placeholder="Code" value={form.code} onChange={e=>setForm({...form, code:e.target.value})} />
          </div>
          <div style={{flex:2}}>
            <input className="input" placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} />
          </div>
          <button className="btn primary">Create</button>
        </form>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Code</th><th>Name</th><th>Status</th></tr></thead>
          <tbody>
            {items.map(p => <tr key={p.id}><td>{p.code}</td><td>{p.name}</td><td>{p.status}</td></tr>)}
          </tbody>
        </table>
      </div>
    </>
  )
}
