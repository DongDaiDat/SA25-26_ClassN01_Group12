import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function Sections() {
  const [sections, setSections] = useState([])
  const [terms, setTerms] = useState([])
  const [courses, setCourses] = useState([])
  const [form, setForm] = useState({ term_id:'', course_id:'', section_code:'A', capacity:30 })
  const [err, setErr] = useState(null)

  const load = async () => {
    const [s,t,c] = await Promise.all([
      core.get('/section/sections/'),
      core.get('/term/terms/'),
      core.get('/course-catalog/courses/'),
    ])
    setSections(s.data?.data||[])
    setTerms(t.data?.data||[])
    setCourses(c.data?.data||[])
  }
  useEffect(()=>{ load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr(null)
    try {
      await core.post('/section/sections/', { ...form, capacity: Number(form.capacity) })
      await load()
    } catch (e) { setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Sections</h2>
        {err && <p className="error">{err}</p>}
        <form onSubmit={submit} className="row">
          <select className="input" style={{flex:1}} value={form.term_id} onChange={e=>setForm({...form, term_id:e.target.value})}>
            <option value="">Select Term</option>
            {terms.map(t => <option key={t.id} value={t.id}>{t.code}</option>)}
          </select>
          <select className="input" style={{flex:2}} value={form.course_id} onChange={e=>setForm({...form, course_id:e.target.value})}>
            <option value="">Select Course</option>
            {courses.map(c => <option key={c.id} value={c.id}>{c.code}</option>)}
          </select>
          <input className="input" style={{width:120}} value={form.section_code} onChange={e=>setForm({...form, section_code:e.target.value})} />
          <input className="input" style={{width:120}} type="number" value={form.capacity} onChange={e=>setForm({...form, capacity:e.target.value})} />
          <button className="btn primary">Create</button>
        </form>
      </div>

      <div className="card">
        <table className="table">
          <thead><tr><th>Term</th><th>Course</th><th>Section</th><th>Cap</th><th>Enrolled</th><th>Status</th></tr></thead>
          <tbody>
            {sections.map(s => (
              <tr key={s.id}>
                <td>{s.term_code}</td>
                <td>{s.course_code}</td>
                <td>{s.section_code}</td>
                <td>{s.capacity}</td>
                <td>{s.enrolled_count}</td>
                <td>{s.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
