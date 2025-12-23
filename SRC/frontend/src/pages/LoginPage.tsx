import { useState, type FormEvent } from "react";
import { api, setToken } from "../api/client";

type Props = {
  onLoggedIn: () => void;
};

function pickErrorMessage(err: unknown): string {
  // Ưu tiên các cấu trúc lỗi hay gặp (fetch/axios/fastapi)
  if (typeof err === "string") return err;

  if (err && typeof err === "object") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e: any = err;

    // axios style: err.response.data.detail
    const detail = e?.response?.data?.detail ?? e?.detail;

    // FastAPI/Pydantic validation: detail là mảng lỗi
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (typeof first === "string") return first;
      if (first?.msg) return String(first.msg);
      return JSON.stringify(first);
    }

    // FastAPI custom: detail là string
    if (typeof detail === "string") return detail;

    // message
    if (typeof e?.message === "string") return e.message;

    // fallback
    try {
      return JSON.stringify(e);
    } catch {
      return "LOGIN_FAILED";
    }
  }

  return "LOGIN_FAILED";
}

export default function LoginPage({ onLoggedIn }: Props) {
  // Vì backend chặn domain .local => dùng domain “thật”
  const DEFAULT_EMAIL = "admin@unimis.edu.vn";
  const DEFAULT_PASSWORD = "Admin@123";

  const [email, setEmail] = useState(DEFAULT_EMAIL);
  const [password, setPassword] = useState(DEFAULT_PASSWORD);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const res = await api.login(email.trim(), password);
      setToken(res.accessToken);
      onLoggedIn();
    } catch (error) {
      setErr(pickErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ maxWidth: 520 }}>
      <h3>Login</h3>

      <form onSubmit={submit} className="row">
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email"
          autoComplete="email"
          style={{ flex: 1, minWidth: 240 }}
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          type="password"
          autoComplete="current-password"
          style={{ flex: 1, minWidth: 200 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      {err && <p className="err">{err}</p>}

      <p className="muted">
        Seed: <code>{DEFAULT_EMAIL}</code> / <code>{DEFAULT_PASSWORD}</code>
      </p>
    </div>
  );
}
