import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'
import { useAuth } from '../state/auth.jsx'

export default function Certificates() {
  const { me } = useAuth()
  const [defs, setDefs] = useState([])
  const [issues, setIssues] = useState([])
  const [form, setForm] = useState({ code:'', name:'', required_course_ids:'', min_grade:5 })
  const [issueReq, setIssueReq] = useState({ definition_id:'', student_id:'' })
  const [verifyCode, setVerifyCode] = useState('')
  const [verifyRes, setVerifyRes] = useState(null)
  const [err, setErr] = useState(null)

  const load = async () => {
    const [d,i] = await Promise.all([
      core.get('/certificate/definitions/'),
      core.get('/certificate/issues/'),
    ])
    setDefs(d.data?.data||[])
    setIssues(i.data?.data||[])
  }
  useEffect(()=>{ load() }, [])

  const createDef = async (e) => {
    e.preventDefault()
    setErr(null)
    try{
      const required_course_ids = form.required_course_ids.split(',').map(x=>x.trim()).filter(Boolean)
      await core.post('/certificate/definitions/', {
        code: form.code, name: form.name,
        rules: { required_course_ids, min_grade: Number(form.min_grade) }
      })
      setForm({ code:'', name:'', required_course_ids:'', min_grade:5 })
      load()
    }catch(e){ setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  const issue = async () => {
    setErr(null)
    try{
      await core.post('/certificate/issues/issue/', issueReq)
      setIssueReq({ definition_id:'', student_id:'' })
      load()
    }catch(e){ setErr(e?.response?.data?.error?.message || 'Failed') }
  }

  const verify = async () => {
    setVerifyRes(null); setErr(null)
    try{
      const r = await core.get(`/certificate/issues/verify/?code=${encodeURIComponent(verifyCode)}`)
      setVerifyRes(r.data)
    }catch(e){ setErr('Verify failed') }
  }

  return (
    <>
      <div className="card">
        <h2>Certificates</h2>
        {err && <p className="error">{err}</p>}
        {['ADMIN','REGISTRAR'].includes(me?.role) && (
          <>
            <h3>Create Definition</h3>
            <form onSubmit={createDef} className="row">
              <input className="input" style={{flex:1}} placeholder="Code" value={form.code} onChange={e=>setForm({...form, code:e.target.value})} />
              <input className="input" style={{flex:2}} placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} />
              <input className="input" style={{flex:3}} placeholder="required_course_ids (comma UUIDs)" value={form.required_course_ids} onChange={e=>setForm({...form, required_course_ids:e.target.value})} />
              <input className="input" style={{width:120}} type="number" placeholder="min_grade" value={form.min_grade} onChange={e=>setForm({...form, min_grade:e.target.value})} />
              <button className="btn primary">Create</button>
            </form>

            <h3>Issue Certificate</h3>
            <div className="row">
              <select className="input" style={{flex:1}} value={issueReq.definition_id} onChange={e=>setIssueReq({...issueReq, definition_id:e.target.value})}>
                <option value="">Select Definition</option>
                {defs.map(d => <option key={d.id} value={d.id}>{d.code}</option>)}
              </select>
              <input className="input" style={{flex:1}} placeholder="student UUID" value={issueReq.student_id} onChange={e=>setIssueReq({...issueReq, student_id:e.target.value})} />
              <button className="btn primary" onClick={issue}>Issue</button>
            </div>
          </>
        )}

        <h3>Verify</h3>
        <div className="row">
          <input className="input" style={{flex:1}} placeholder="verify code" value={verifyCode} onChange={e=>setVerifyCode(e.target.value)} />
          <button className="btn" onClick={verify}>Verify</button>
        </div>
        {verifyRes && <pre>{JSON.stringify(verifyRes, null, 2)}</pre>}
      </div>

      <div className="card">
        <h3>Definitions</h3>
        <table className="table">
          <thead><tr><th>Code</th><th>Name</th><th>Rules</th></tr></thead>
          <tbody>
            {defs.map(d => <tr key={d.id}><td>{d.code}</td><td>{d.name}</td><td><pre style={{margin:0}}>{JSON.stringify(d.rules)}</pre></td></tr>)}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Issued</h3>
        <table className="table">
          <thead><tr><th>Definition</th><th>Student</th><th>Verify code</th><th>Status</th></tr></thead>
          <tbody>
            {issues.map(i => <tr key={i.id}><td>{i.definition_code}</td><td>{i.student_username}</td><td>{i.verify_code}</td><td>{i.status}</td></tr>)}
          </tbody>
        </table>
      </div>
    </>
  )
}
