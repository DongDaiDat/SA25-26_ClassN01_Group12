import React, { useEffect, useState } from 'react'
import { core } from '../api/client.js'

export default function Grades() {
  const [grades, setGrades] = useState([])
  useEffect(()=>{ core.get('/assessment/grades/').then(r=>setGrades(r.data?.data||[])) }, [])
  return (
    <div className="card">
      <h2>Grades</h2>
      <table className="table">
        <thead><tr><th>Course</th><th>Section</th><th>Grade</th><th>Status</th></tr></thead>
        <tbody>
          {grades.map(g => (
            <tr key={g.id}>
              <td>{g.course_id}</td>
              <td>{g.section_id}</td>
              <td>{g.grade_value ?? '-'}</td>
              <td>{g.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
