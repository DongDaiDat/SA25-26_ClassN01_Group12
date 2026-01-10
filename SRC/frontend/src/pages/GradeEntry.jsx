import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function GradeEntry() {
  const [sections, setSections] = useState([])
  const [sectionId, setSectionId] = useState('')
  const [rows, setRows] = useState([{ student_id:'', grade_value:'' }])
  const [msg, setMsg] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(()=>{ core.get('/section/sections/').then(r=>setSections(r.data?.data||[])) }, [])

  const addRow = () => setRows([...rows, { student_id:'', grade_value:'' }])

  const save = async () => {
    setErr(null); setMsg(null)
    try{
      const grades = rows.filter(r=>r.student_id).map(r=>({ student_id: r.student_id, grade_value: r.grade_value===''? null : Number(r.grade_value) }))
      await core.post('/assessment/grades/bulk_enter/', { section_id: sectionId, grades })
      setMsg('Saved')
    }catch(e){ setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  const publish = async () => {
    setErr(null); setMsg(null)
    try{
      await core.post('/assessment/grades/publish/', { section_id: sectionId })
      setMsg('Published')
    }catch(e){ setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Grade Entry</h2>
        {err && <p className="error">{err}</p>}
        {msg && <p>{msg}</p>}
        <select className="input" value={sectionId} onChange={e=>setSectionId(e.target.value)}>
          <option value="">Select Section</option>
          {sections.map(s => <option key={s.id} value={s.id}>{s.term_code} · {s.course_code} · {s.section_code}</option>)}
        </select>
        <div style={{height:10}} />
        <div className="card" style={{background:'#fafafa'}}>
          {rows.map((r, idx)=>(
            <div key={idx} className="row" style={{marginBottom:8}}>
              <input className="input" style={{flex:2}} placeholder="student UUID" value={r.student_id} onChange={e=>{
                const next=[...rows]; next[idx]={...r, student_id:e.target.value}; setRows(next)
              }} />
              <input className="input" style={{width:120}} placeholder="grade" value={r.grade_value} onChange={e=>{
                const next=[...rows]; next[idx]={...r, grade_value:e.target.value}; setRows(next)
              }} />
            </div>
          ))}
          <button className="btn" onClick={addRow}>+ Row</button>
        </div>
        <div className="row">
          <button className="btn primary" onClick={save} disabled={!sectionId}>Save Draft</button>
          <button className="btn" onClick={publish} disabled={!sectionId}>Publish</button>
        </div>
        <p style={{fontSize:12, opacity:0.8}}>Tip: Use student UUID from Admin /auth/users/ (admin role) or DB for quick demo.</p>
      </div>
    </>
  )
}
