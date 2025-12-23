import { useMemo, useState } from "react";import Nav, { Page } from "./components/Nav";
import LoginPage from "./pages/LoginPage";
import ProgramsPage from "./pages/ProgramsPage";
import CoursesPage from "./pages/CoursesPage";
import WorkflowPage from "./pages/WorkflowPage";
import ReportsPage from "./pages/ReportsPage";
import SisPage from "./pages/SisPage";
import { getToken, setToken } from "./api/client";

export default function App() {
  const [page, setPage] = useState<Page>(getToken() ? "programs" : "login");

  function logout() {
    setToken(null);
    setPage("login");
  }

  const content = useMemo(() => {
    if (page === "login") return <LoginPage onLoggedIn={() => setPage("programs")} />;
    if (page === "programs") return <ProgramsPage />;
    if (page === "courses") return <CoursesPage />;
    if (page === "workflow") return <WorkflowPage />;
    if (page === "reports") return <ReportsPage />;
    if (page === "sis") return <SisPage />;
    return null;
  }, [page]);

  return (
    <div className="app">
      <div className="side">
        {page === "login" ? (
          <div>
            <h2 style={{ margin: 0 }}>UniMIS</h2>
            <p className="muted">Vui lòng đăng nhập</p>
          </div>
        ) : (
          <Nav page={page} setPage={setPage} onLogout={logout} />
        )}
      </div>
      <div className="main">{content}</div>
    </div>
  );
}
