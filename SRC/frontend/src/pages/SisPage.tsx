import { useState } from "react";import { api } from "../api/client";

export default function SisPage() {
  const [program_id, setProgramId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [res, setRes] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function importCsv() {
    setErr(null);
    try {
      if (!program_id) return alert("Nhập program_id");
      if (!file) return alert("Chọn file CSV");
      const r = await api.importStudentsCSV(program_id, file);
      setRes(r);
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div>
      <h3>SIS</h3>

      <div className="card">
        <h4>Import Students CSV</h4>
        <p className="muted">Header: <code>student_code,full_name,email</code></p>
        <div className="row">
          <input value={program_id} onChange={(e) => setProgramId(e.target.value)} placeholder="program_id" style={{ minWidth: 360 }} />
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button onClick={importCsv}>Import</button>
        </div>

        {res && (
          <pre style={{ background: "#f6f6f6", padding: 12, borderRadius: 10, overflowX: "auto", marginTop: 10 }}>
{JSON.stringify(res, null, 2)}
          </pre>
        )}
      </div>

      {err && <p className="err">{err}</p>}
    </div>
  );
}
