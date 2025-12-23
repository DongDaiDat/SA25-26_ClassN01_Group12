import { useState } from "react";import { api } from "../api/client";

export default function WorkflowPage() {
  const [workflow_code, setWorkflow] = useState("PROGRAM_CREATE");
  const [target_type, setTargetType] = useState("PROGRAM");
  const [target_id, setTargetId] = useState("");
  const [title, setTitle] = useState("Tạo CTĐT mới (demo)");
  const [payload, setPayload] = useState("{\n  \"foo\": \"bar\"\n}");
  const [crId, setCrId] = useState("");
  const [cr, setCr] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function createCR() {
    setErr(null);
    try {
      const p = JSON.parse(payload);
      const res = await api.createCR({ workflow_code, target_type, target_id, title, description: null, payload: p });
      setCrId(res.cr_id);
      setCr(res);
    } catch (e: any) { setErr(e.message); }
  }

  async function loadCR() {
    setErr(null);
    try {
      const res = await api.getCR(crId);
      setCr(res);
    } catch (e: any) { setErr(e.message); }
  }

  async function act(action: "approve"|"need"|"reject") {
    setErr(null);
    try {
      if (!crId) return;
      const step_no = Number(prompt("Step no?", String(cr?.current_step_no ?? 1)) || "1");
      const comment = prompt("Comment (optional)") || undefined;

      if (action === "approve") await api.approveCR(crId, step_no, comment);
      if (action === "need") await api.needMoreInfoCR(crId, step_no, comment);
      if (action === "reject") await api.rejectCR(crId, step_no, comment);

      await loadCR();
    } catch (e: any) { setErr(e.message); }
  }

  async function resubmit() {
    setErr(null);
    try {
      if (!crId) return;
      const patchStr = prompt("Payload patch JSON", "{\n  \"more\": \"info\"\n}") || "{}";
      const patch = JSON.parse(patchStr);
      await api.resubmitCR(crId, patch);
      await loadCR();
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div>
      <h3>Workflow</h3>

      <div className="card">
        <h4>Tạo Change Request</h4>
        <div className="row">
          <select value={workflow_code} onChange={(e) => setWorkflow(e.target.value)}>
            <option value="PROGRAM_CREATE">PROGRAM_CREATE</option>
            <option value="PROGRAM_PUBLISH">PROGRAM_PUBLISH</option>
            <option value="SYLLABUS_PUBLISH">SYLLABUS_PUBLISH</option>
          </select>
          <input value={target_type} onChange={(e) => setTargetType(e.target.value)} placeholder="target_type" />
          <input value={target_id} onChange={(e) => setTargetId(e.target.value)} placeholder="target_id (UUID)" style={{ minWidth: 360 }} />
        </div>
        <div className="row" style={{ marginTop: 8 }}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="title" style={{ flex: 1, minWidth: 420 }} />
          <button onClick={createCR}>Create CR</button>
        </div>
        <textarea value={payload} onChange={(e) => setPayload(e.target.value)} rows={6} style={{ width: "100%", marginTop: 8 }} />
      </div>

      <div className="card">
        <h4>Tra cứu & duyệt</h4>
        <div className="row">
          <input value={crId} onChange={(e) => setCrId(e.target.value)} placeholder="cr_id" style={{ minWidth: 360 }} />
          <button onClick={loadCR}>Load</button>
          <button onClick={() => act("approve")}>Approve</button>
          <button onClick={() => act("need")}>Need more info</button>
          <button onClick={() => act("reject")}>Reject</button>
          <button onClick={resubmit}>Resubmit</button>
        </div>

        {cr && (
          <pre style={{ background: "#f6f6f6", padding: 12, borderRadius: 10, overflowX: "auto" }}>
{JSON.stringify(cr, null, 2)}
          </pre>
        )}
      </div>

      {err && <p className="err">{err}</p>}
    </div>
  );
}
