import React, { useEffect, useMemo, useState } from 'react'
import { core } from '../api/client.js'

export default function GradeEntry() {
  const [sections, setSections] = useState([])
  const [sectionId, setSectionId] = useState('')
  const [rows, setRows] = useState([]) // { student_id, student_username, grade_value }
  const [msg, setMsg] = useState(null)
  const [err, setErr] = useState(null)
  const [loadingSections, setLoadingSections] = useState(false)
  const [loadingRoster, setLoadingRoster] = useState(false)
  const [saving, setSaving] = useState(false)
  const [publishing, setPublishing] = useState(false)

  const selectedSection = useMemo(
    () => sections.find((s) => String(s.id) === String(sectionId)),
    [sections, sectionId]
  )

  const normalizeList = (payload) => {
    // hỗ trợ cả dạng {data:[...]} và dạng [...]
    if (!payload) return []
    if (Array.isArray(payload)) return payload
    if (Array.isArray(payload.data)) return payload.data
    return []
  }

  // Load sections
  useEffect(() => {
    let mounted = true
    setLoadingSections(true)
    core
      .get('/section/sections/')
      .then((r) => {
        if (!mounted) return
        const list = normalizeList(r?.data)
        setSections(list)
        if (!sectionId && list.length > 0) setSectionId(String(list[0].id))
      })
      .catch(() => mounted && setErr('Cannot load sections'))
      .finally(() => mounted && setLoadingSections(false))

    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Load roster theo sectionId
  useEffect(() => {
    let mounted = true

    const loadRoster = async () => {
      if (!sectionId) {
        setRows([])
        return
      }

      setErr(null)
      setMsg(null)
      setLoadingRoster(true)

      try {
        // ✅ FIX: backend đang expose url_path="by-section"
        const r = await core.get('/enrollment/enrollments/by-section/', {
          params: { section_id: sectionId },
        })

        const enrollments = normalizeList(r?.data)

        // EnrollmentSerializer trả: student (int) + student_username
        const rosterRows = enrollments
          .map((e) => {
            const sidRaw = e?.student ?? e?.student_id
            const sid = Number(sidRaw)
            if (!Number.isFinite(sid) || sid <= 0) return null
            return {
              student_id: sid,
              student_username: e?.student_username || `ID:${sid}`,
              grade_value: '',
            }
          })
          .filter(Boolean)

        if (!mounted) return
        setRows(rosterRows)
        if (rosterRows.length === 0) setErr('Roster is empty (no ACTIVE enrollments in this section)')
      } catch (e) {
        if (!mounted) return
        const message =
          e?.response?.data?.detail ||
          e?.response?.data?.error?.message ||
          'Cannot load roster (check permission / endpoint)'
        setErr(message)
        setRows([])
      } finally {
        if (!mounted) return
        setLoadingRoster(false)
      }
    }

    loadRoster()
    return () => {
      mounted = false
    }
  }, [sectionId])

  const updateRow = (idx, patch) => {
    setRows((prev) => {
      const next = [...prev]
      next[idx] = { ...next[idx], ...patch }
      return next
    })
  }

  const validateBeforeSend = () => {
    // grade_value: '' hoặc number 0..10
    for (const r of rows) {
      const sid = Number(r.student_id)
      if (!Number.isFinite(sid) || sid <= 0) {
        setErr('Invalid student_id in roster. Please re-load roster.')
        return false
      }
      if (r.grade_value !== '') {
        const gv = Number(r.grade_value)
        if (!Number.isFinite(gv)) {
          setErr(`Invalid grade for ${r.student_username}. Grade must be a number.`)
          return false
        }
        if (gv < 0 || gv > 10) {
          setErr(`Invalid grade for ${r.student_username}. Grade must be between 0 and 10.`)
          return false
        }
      }
    }
    return true
  }

  const buildPayload = () => {
    const grades = rows.map((r) => ({
      student_id: Number(r.student_id), // ✅ luôn là số
      grade_value: r.grade_value === '' ? null : Number(r.grade_value),
    }))
    return { section_id: sectionId, grades }
  }

  const save = async () => {
    setErr(null)
    setMsg(null)
    if (!sectionId) return
    if (!validateBeforeSend()) return

    setSaving(true)
    try {
      await core.post('/assessment/grades/bulk_enter/', buildPayload())
      setMsg('Saved')
    } catch (e) {
      const details = e?.response?.data?.error?.details
      const message = e?.response?.data?.detail || e?.response?.data?.error?.message || 'Failed'
      setErr(details ? `${message}: ${JSON.stringify(details)}` : message)
    } finally {
      setSaving(false)
    }
  }

  const publish = async () => {
    setErr(null)
    setMsg(null)
    if (!sectionId) return

    setPublishing(true)
    try {
      await core.post('/assessment/grades/publish/', { section_id: sectionId })
      setMsg('Published')
    } catch (e) {
      const details = e?.response?.data?.error?.details
      const message = e?.response?.data?.detail || e?.response?.data?.error?.message || 'Failed'
      setErr(details ? `${message}: ${JSON.stringify(details)}` : message)
    } finally {
      setPublishing(false)
    }
  }

  return (
    <div className="card">
      <h2>Grade Entry</h2>

      {err && <p className="error">{err}</p>}
      {msg && <p>{msg}</p>}

      <select
        className="input"
        value={sectionId}
        onChange={(e) => setSectionId(e.target.value)}
        disabled={loadingSections}
      >
        <option value="">{loadingSections ? 'Loading sections...' : 'Select Section'}</option>
        {sections.map((s) => (
          <option key={s.id} value={s.id}>
            {s.term_code} · {s.course_code} · {s.section_code}
          </option>
        ))}
      </select>

      <div style={{ height: 10 }} />

      <div className="card" style={{ background: '#fafafa' }}>
        {loadingRoster && sectionId ? (
          <p style={{ fontSize: 12, opacity: 0.8, marginTop: 0 }}>
            Loading roster for <b>{selectedSection?.course_code}</b>...
          </p>
        ) : null}

        {rows.length === 0 && !loadingRoster ? (
          <p style={{ fontSize: 12, opacity: 0.8, marginTop: 0 }}>
            No roster loaded. Ensure there are ACTIVE enrollments for this section.
          </p>
        ) : null}

        {rows.map((r, idx) => (
          <div key={`${r.student_id}-${idx}`} className="row" style={{ marginBottom: 8 }}>
            <div className="input" style={{ flex: 2, display: 'flex', alignItems: 'center' }}>
              <b style={{ marginRight: 8 }}>{r.student_username}</b>
              <span style={{ fontSize: 12, opacity: 0.7 }}>ID: {r.student_id}</span>
            </div>

            <input
              className="input"
              style={{ width: 120 }}
              placeholder="grade 0-10"
              value={r.grade_value}
              onChange={(e) => updateRow(idx, { grade_value: e.target.value })}
            />
          </div>
        ))}
      </div>

      <div className="row">
        <button className="btn primary" onClick={save} disabled={!sectionId || saving || loadingRoster}>
          {saving ? 'Saving...' : 'Save Draft'}
        </button>
        <button className="btn" onClick={publish} disabled={!sectionId || publishing || loadingRoster}>
          {publishing ? 'Publishing...' : 'Publish'}
        </button>
      </div>

      <p style={{ fontSize: 12, opacity: 0.8 }}>
        Roster endpoint: <code>/enrollment/enrollments/by-section/?section_id=...</code>
      </p>
    </div>
  )
}
