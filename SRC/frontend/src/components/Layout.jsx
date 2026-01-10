import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../state/auth.jsx'

export default function Layout({ children }) {
  const { me, logout } = useAuth()
  return (
    <>
      <div className="nav">
        <div className="container">
          <div style={{display:'flex', gap:10, alignItems:'center'}}>
            <b>TPMS</b>
            {me && <span className="badge">{me.username} · {me.role}</span>}
          </div>
          <div className="nav-links">
            {me && <>
              <Link to="/">Dashboard</Link>
              {['ADMIN','REGISTRAR','MANAGER'].includes(me.role) && <>
                <Link to="/programs">Programs</Link>
                <Link to="/courses">Courses</Link>
                <Link to="/sections">Sections</Link>
              </>}
              {me.role === 'STUDENT' && <Link to="/enrollment">Enrollment</Link>}
              {['INSTRUCTOR','ADMIN','REGISTRAR'].includes(me.role) && <Link to="/grade-entry">Grade Entry</Link>}
              <Link to="/grades">Grades</Link>
              <Link to="/certificates">Certificates</Link>
              <Link to="/notifications">Notifications</Link>
              <button className="btn" onClick={logout}>Logout</button>
            </>}
            {!me && <Link to="/login">Login</Link>}
          </div>
        </div>
      </div>
      <div className="container">{children}</div>
    </>
  )
}
