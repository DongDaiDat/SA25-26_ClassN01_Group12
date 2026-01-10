import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Programs from './pages/Programs.jsx'
import Courses from './pages/Courses.jsx'
import Sections from './pages/Sections.jsx'
import Enrollment from './pages/Enrollment.jsx'
import Grades from './pages/Grades.jsx'
import GradeEntry from './pages/GradeEntry.jsx'
import Certificates from './pages/Certificates.jsx'
import Notifications from './pages/Notifications.jsx'
import { useAuth } from './state/auth.jsx'
import { core } from './api/client.js'

function Protected({ children }) {
  const { me } = useAuth()
  if (!me) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const { me, setMe } = useAuth()

  // restore session on refresh if tokens exist
  useEffect(() => {
    const raw = localStorage.getItem('tpms_tokens')
    const t = raw ? JSON.parse(raw) : null
    if (t?.access && !me) {
      core.get('/auth/whoami/').then(r => setMe(r.data?.data)).catch(()=>{})
    }
  }, [])

  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Protected><Dashboard /></Protected>} />
        <Route path="/programs" element={<Protected><Programs /></Protected>} />
        <Route path="/courses" element={<Protected><Courses /></Protected>} />
        <Route path="/sections" element={<Protected><Sections /></Protected>} />
        <Route path="/enrollment" element={<Protected><Enrollment /></Protected>} />
        <Route path="/grades" element={<Protected><Grades /></Protected>} />
        <Route path="/grade-entry" element={<Protected><GradeEntry /></Protected>} />
        <Route path="/certificates" element={<Protected><Certificates /></Protected>} />
        <Route path="/notifications" element={<Protected><Notifications /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
