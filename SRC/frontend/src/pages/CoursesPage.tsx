import { useEffect, useState } from "react";import { api } from "../api/client";

export default function CoursesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const [course_code, setCode] = useState("CS101");
  const [name_vi, setVi] = useState("Nhập môn lập trình");
  const [name_en, setEn] = useState("Introduction to Programming");
  const [credits, setCredits] = useState<number>(3);
  const [unit_id, setUnitId] = useState("");

  const [selectedCourse, setSelectedCourse] = useState<string>("");

  async function load() {
    setErr(null);
    try {
      const data = await api.listCourses();
      setRows(data);
      if (!selectedCourse && data?.[0]?.course_id) setSelectedCourse(data[0].course_id);
      if (!unit_id && data?.[0]?.unit_id) setUnitId(data[0].unit_id);
    } catch (e: any) { setErr(e.message); }
  }

  useEffect(() => { load(); }, []);

  async function createCourse() {
    setErr(null);
    try {
      if (!unit_id) return alert("unit_id trống. Dùng unit_id của UNI hoặc lấy từ program.");
      await api.createCourse({ course_code, name_vi, name_en, credits, unit_id });
      await load();
    } catch (e: any) { setErr(e.message); }
  }

  async function createVersion() {
    setErr(null);
    try {
      if (!selectedCourse) return;
      const res = await api.createCourseVersion(selectedCourse, "Đề cương VI (demo)", "Syllabus EN (demo)");
      alert("Tạo course version OK: " + JSON.stringify(res));
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div>
      <h3>Courses</h3>

      <div className="card">
        <h4>Tạo Course</h4>
        <div className="row">
          <input value={course_code} onChange={(e) => setCode(e.target.value)} placeholder="course_code" />
          <input value={name_vi} onChange={(e) => setVi(e.target.value)} placeholder="name_vi" style={{ minWidth: 240 }} />
          <input value={name_en} onChange={(e) => setEn(e.target.value)} placeholder="name_en" style={{ minWidth: 240 }} />
          <input type="number" value={credits} onChange={(e) => setCredits(Number(e.target.value))} placeholder="credits" />
          <input value={unit_id} onChange={(e) => setUnitId(e.target.value)} placeholder="unit_id (UUID)" style={{ minWidth: 320 }} />
          <button onClick={createCourse}>Create</button>
        </div>
      </div>

      <div className="card">
        <h4>Tạo Course Version</h4>
        <div className="row">
          <select value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)}>
            {rows.map((r) => <option key={r.course_id} value={r.course_id}>{r.course_code} — {r.name_vi}</option>)}
          </select>
          <button onClick={createVersion}>Create Version</button>
        </div>
      </div>

      {err && <p className="err">{err}</p>}

      <div className="card">
        <h4>Danh sách</h4>
        <table>
          <thead><tr><th>Code</th><th>Name (VI)</th><th>Credits</th><th>Unit</th><th>ID</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.course_id}>
                <td>{r.course_code}</td>
                <td>{r.name_vi}</td>
                <td>{r.credits}</td>
                <td className="muted">{r.unit_id}</td>
                <td className="muted">{r.course_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
