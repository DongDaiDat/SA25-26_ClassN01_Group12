
export type Page = "login" | "programs" | "courses" | "workflow" | "reports" | "sis";

export default function Nav(props: { page: Page; setPage: (p: Page) => void; onLogout: () => void }) {
  const { page, setPage, onLogout } = props;
  const Item = (p: Page, label: string) => (
    <div style={{ margin: "8px 0" }}>
      <button
        onClick={() => setPage(p)}
        style={{ width: "100%", textAlign: "left", background: page === p ? "#eee" : "white" }}
      >
        {label}
      </button>
    </div>
  );

  return (
    <div>
      <h2 style={{ margin: 0 }}>UniMIS</h2>
      <p className="muted">MVP demo</p>
      {Item("programs", "Programs")}
      {Item("courses", "Courses")}
      {Item("workflow", "Workflow")}
      {Item("reports", "Reports (MOET)")}
      {Item("sis", "SIS")}
      <hr />
      <button onClick={onLogout} style={{ width: "100%" }}>Logout</button>
    </div>
  );
}
