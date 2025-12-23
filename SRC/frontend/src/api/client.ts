const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

export function getToken(): string | null {
  return localStorage.getItem("accessToken");
}
export function setToken(token: string | null) {
  if (!token) localStorage.removeItem("accessToken");
  else localStorage.setItem("accessToken", token);
}

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { ...(init.headers as any) };
  if (!(init.body instanceof FormData)) headers["Content-Type"] = headers["Content-Type"] || "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const text = await res.text();
  let json: any = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = null; }

  if (!res.ok) throw new Error(json?.detail || res.statusText);
  if (json?.success === false) throw new Error(json?.error?.message || "API_ERROR");
  return json?.data ?? json;
}

export const api = {
  login: (email: string, password: string) =>
    req<{ accessToken: string; tokenType: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  listPrograms: () => req<any[]>("/programs"),
  createProgram: (payload: any) => req<any>("/programs", { method: "POST", body: JSON.stringify(payload) }),
  createProgramVersion: (program_id: string, apply_year: number, copy_from_latest: boolean) =>
    req<any>(`/programs/${program_id}/versions`, { method: "POST", body: JSON.stringify({ apply_year, copy_from_latest }) }),

  listCourses: () => req<any[]>("/courses"),
  createCourse: (payload: any) => req<any>("/courses", { method: "POST", body: JSON.stringify(payload) }),
  createCourseVersion: (course_id: string, vi?: string, en?: string) =>
    req<any>(`/courses/${course_id}/versions`, { method: "POST", body: JSON.stringify({ syllabus_text_vi: vi ?? null, syllabus_text_en: en ?? null }) }),

  createCR: (payload: any) => req<any>("/change-requests", { method: "POST", body: JSON.stringify(payload) }),
  getCR: (cr_id: string) => req<any>(`/change-requests/${cr_id}`),
  approveCR: (cr_id: string, step_no: number, comment?: string) =>
    req<any>(`/change-requests/${cr_id}/approve`, { method: "POST", body: JSON.stringify({ step_no, comment: comment ?? null }) }),
  needMoreInfoCR: (cr_id: string, step_no: number, comment?: string) =>
    req<any>(`/change-requests/${cr_id}/need-more-info`, { method: "POST", body: JSON.stringify({ step_no, comment: comment ?? null }) }),
  rejectCR: (cr_id: string, step_no: number, comment?: string) =>
    req<any>(`/change-requests/${cr_id}/reject`, { method: "POST", body: JSON.stringify({ step_no, comment: comment ?? null }) }),
  resubmitCR: (cr_id: string, patch: any) =>
    req<any>(`/change-requests/${cr_id}/resubmit`, { method: "POST", body: JSON.stringify(patch) }),

  uploadTemplate: async (template_code: string, name: string, version: number, file: File) => {
    const fd = new FormData();
    fd.append("template_code", template_code);
    fd.append("name", name);
    fd.append("version", String(version));
    fd.append("file", file);
    return req<any>("/reports/templates/upload", { method: "POST", body: fd });
  },

  exportMOET: (program_version_id: string, template_code: string) =>
    req<any>("/reports/moet/export", { method: "POST", body: JSON.stringify({ program_version_id, template_code }) }),

  importStudentsCSV: async (program_id: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return req<any>(`/sis/students/import?program_id=${encodeURIComponent(program_id)}`, { method: "POST", body: fd });
  },

  downloadFileUrl: (file_id: string) => `${API_BASE}/files/${file_id}/download`,
};
