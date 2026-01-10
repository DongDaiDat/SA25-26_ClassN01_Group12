import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function Enrollment() {
  const [sections, setSections] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [err, setErr] = useState(null)

  const load = async () => {
    const [s,e] = await Promise.all([
      core.get('/section/sections/'),
      core.get('/enrollment/enrollments/'),
    ])
    setSections(s.data?.data||[])
    setEnrollments(e.data?.data||[])
  }

  useEffect(()=>{ load() }, [])

  const enroll = async (sectionId) => {
    setErr(null)
    try {
      await core.post('/enrollment/enrollments/', { section_id: sectionId }, { headers: { 'Idempotency-Key': crypto.randomUUID() }})
      await load()
    } catch (e) { setErr(e?.response?.data?.error?.message || 'Enroll failed') }
  }

  const cancel = async (enrollmentId) => {
    setErr(null)
    try {
      await core.delete(`/enrollment/enrollments/${enrollmentId}/`)
      await load()
    } catch (e) { setErr(e?.response?.data?.error?.message || 'Cancel failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Enrollment</h2>
        {err && <p className="error">{err}</p>}
        <h3>Available Sections</h3>
        <table className="table">
          <thead><tr><th>Term</th><th>Course</th><th>Section</th><th>Cap</th><th>Enrolled</th><th></th></tr></thead>
          <tbody>
            {sections.map(s => (
              <tr key={s.id}>
                <td>{s.term_code}</td><td>{s.course_code}</td><td>{s.section_code}</td><td>{s.capacity}</td><td>{s.enrolled_count}</td>
                <td><button className="btn primary" onClick={()=>enroll(s.id)}>Enroll</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>My Enrollments</h3>
        <table className="table">
          <thead><tr><th>Status</th><th>Section</th><th>Created</th><th></th></tr></thead>
          <tbody>
            {enrollments.map(e => (
              <tr key={e.id}>
                <td>{e.status}</td><td>{e.section_id}</td><td>{new Date(e.created_at).toLocaleString()}</td>
                <td>{e.status==='ACTIVE' && <button className="btn danger" onClick={()=>cancel(e.id)}>Cancel</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
