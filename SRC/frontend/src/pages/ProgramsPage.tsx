import { useEffect, useState } from "react";import { api } from "../api/client";

export default function ProgramsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const [program_code, setCode] = useState("IT-01");
  const [name_vi, setVi] = useState("Công nghệ thông tin");
  const [name_en, setEn] = useState("Information Technology");
  const [level, setLevel] = useState("Bachelor");
  const [unit_id, setUnitId] = useState("");

  const [applyYear, setApplyYear] = useState<number>(2026);
  const [selectedProgram, setSelectedProgram] = useState<string>("");

  async function load() {
    setErr(null);
    try {
      const data = await api.listPrograms();
      setRows(data);
      if (!selectedProgram && data?.[0]?.program_id) setSelectedProgram(data[0].program_id);
      if (!unit_id && data?.[0]?.unit_id) setUnitId(data[0].unit_id);
    } catch (e: any) { setErr(e.message); }
  }

  useEffect(() => { load(); }, []);

  async function createProgram() {
    setErr(null);
    try {
      if (!unit_id) return alert("unit_id trống. Mẹo: tạo program qua Swagger để lấy unit_id (UNI) rồi dán vào.");
      await api.createProgram({ program_code, name_vi, name_en, level, unit_id });
      await load();
    } catch (e: any) { setErr(e.message); }
  }

  async function createVersion() {
    setErr(null);
    try {
      if (!selectedProgram) return;
      const res = await api.createProgramVersion(selectedProgram, applyYear, true);
      alert("Tạo version OK: " + JSON.stringify(res));
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div>
      <h3>Programs</h3>

      <div className="card">
        <h4>Tạo Program</h4>
        <div className="row">
          <input value={program_code} onChange={(e) => setCode(e.target.value)} placeholder="program_code" />
          <input value={name_vi} onChange={(e) => setVi(e.target.value)} placeholder="name_vi" style={{ minWidth: 240 }} />
          <input value={name_en} onChange={(e) => setEn(e.target.value)} placeholder="name_en" style={{ minWidth: 240 }} />
          <input value={level} onChange={(e) => setLevel(e.target.value)} placeholder="level" />
          <input value={unit_id} onChange={(e) => setUnitId(e.target.value)} placeholder="unit_id (UUID)" style={{ minWidth: 320 }} />
          <button onClick={createProgram}>Create</button>
        </div>
      </div>

      <div className="card">
        <h4>Tạo Program Version</h4>
        <div className="row">
          <select value={selectedProgram} onChange={(e) => setSelectedProgram(e.target.value)}>
            {rows.map((r) => <option key={r.program_id} value={r.program_id}>{r.program_code} — {r.name_vi}</option>)}
          </select>
          <input type="number" value={applyYear} onChange={(e) => setApplyYear(Number(e.target.value))} />
          <button onClick={createVersion}>Create Version</button>
        </div>
      </div>

      {err && <p className="err">{err}</p>}

      <div className="card">
        <h4>Danh sách</h4>
        <table>
          <thead><tr><th>Code</th><th>Name (VI)</th><th>Level</th><th>Unit</th><th>ID</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.program_id}>
                <td>{r.program_code}</td>
                <td>{r.name_vi}</td>
                <td>{r.level}</td>
                <td className="muted">{r.unit_id}</td>
                <td className="muted">{r.program_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
