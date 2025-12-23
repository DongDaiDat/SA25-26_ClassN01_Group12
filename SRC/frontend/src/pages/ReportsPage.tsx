import { useState } from "react";import { api } from "../api/client";

export default function ReportsPage() {
  const [template_code, setCode] = useState("MOET_DEMO");
  const [name, setName] = useState("MOET Template Demo");
  const [version, setVersion] = useState(1);
  const [file, setFile] = useState<File | null>(null);

  const [program_version_id, setPV] = useState("");
  const [exportRes, setExportRes] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function upload() {
    setErr(null);
    try {
      if (!file) return alert("Chọn file .docx template");
      const res = await api.uploadTemplate(template_code, name, version, file);
      alert("Upload OK: " + JSON.stringify(res));
    } catch (e: any) { setErr(e.message); }
  }

  async function exportPdf() {
    setErr(null);
    try {
      if (!program_version_id) return alert("Nhập program_version_id");
      const res = await api.exportMOET(program_version_id, template_code);
      setExportRes(res);
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div>
      <h3>Reports (MOET)</h3>

      <div className="card">
        <h4>Upload Template (.docx)</h4>
        <div className="row">
          <input value={template_code} onChange={(e) => setCode(e.target.value)} placeholder="template_code" />
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="name" style={{ minWidth: 260 }} />
          <input type="number" value={version} onChange={(e) => setVersion(Number(e.target.value))} />
          <input type="file" accept=".docx" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button onClick={upload}>Upload</button>
        </div>
      </div>

      <div className="card">
        <h4>Export MOET (Word → PDF)</h4>
        <div className="row">
          <input value={program_version_id} onChange={(e) => setPV(e.target.value)} placeholder="program_version_id" style={{ minWidth: 360 }} />
          <button onClick={exportPdf}>Export</button>
        </div>

        {exportRes && (
          <div style={{ marginTop: 10 }}>
            <p className="ok">Export OK</p>
            <div className="row">
              <a href={api.downloadFileUrl(exportRes.output_docx_file_id)} target="_blank">Download DOCX</a>
              <a href={api.downloadFileUrl(exportRes.output_pdf_file_id)} target="_blank">Download PDF</a>
            </div>
            <pre style={{ background: "#f6f6f6", padding: 12, borderRadius: 10, overflowX: "auto" }}>
{JSON.stringify(exportRes, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {err && <p className="err">{err}</p>}
    </div>
  );
}
