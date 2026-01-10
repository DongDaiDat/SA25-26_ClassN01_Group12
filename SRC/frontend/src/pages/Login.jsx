import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../state/auth.jsx'

export default function Login() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState('student')
  const [password, setPassword] = useState('student123')
  const [err, setErr] = useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setErr(null)
    try {
      await login(username, password)
      nav('/')
    } catch (e) {
      setErr(e?.response?.data?.error?.message || 'Login failed')
    }
  }

  return (
    <div className="card" style={{maxWidth:420, margin:'40px auto'}}>
      <h2>Login</h2>
      <p>Dev accounts: admin/admin123, registrar/registrar123, instructor/instructor123, student/student123</p>
      {err && <p className="error">{err}</p>}
      <form onSubmit={submit}>
        <label>Username</label>
        <input className="input" value={username} onChange={e=>setUsername(e.target.value)} />
        <div style={{height:8}} />
        <label>Password</label>
        <input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <div style={{height:12}} />
        <button className="btn primary" type="submit">Login</button>
      </form>
    </div>
  )
}
