import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function Courses() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ code:'', name:'', credits:3, status:'ACTIVE' })
  const [err, setErr] = useState(null)

  const load = () => core.get('/course-catalog/courses/').then(r=>setItems(r.data?.data||[]))
  useEffect(()=>{ load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr(null)
    try {
      await core.post('/course-catalog/courses/', {...form, credits: Number(form.credits) })
      setForm({ code:'', name:'', credits:3, status:'ACTIVE' })
      load()
    } catch (e) { setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Courses</h2>
        {err && <p className="error">{err}</p>}
        <form onSubmit={submit} className="row">
          <div style={{flex:1}}><input className="input" placeholder="Code" value={form.code} onChange={e=>setForm({...form, code:e.target.value})} /></div>
          <div style={{flex:2}}><input className="input" placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} /></div>
          <div style={{width:120}}><input className="input" type="number" placeholder="Credits" value={form.credits} onChange={e=>setForm({...form, credits:e.target.value})} /></div>
          <button className="btn primary">Create</button>
        </form>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Code</th><th>Name</th><th>Credits</th></tr></thead>
          <tbody>
            {items.map(c => <tr key={c.id}><td>{c.code}</td><td>{c.name}</td><td>{c.credits}</td></tr>)}
          </tbody>
        </table>
      </div>
    </>
  )
}
