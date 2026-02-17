import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "20s", target: 50 },
    { duration: "40s", target: 150 },
    { duration: "40s", target: 400 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],      // <5% fail (vì có write/publish)
    http_req_duration: ["p(95)<2000"],   // p95 < 2s (local docker)
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const CORE = `${BASE}/api/v1`;
const NOTI = `${BASE}/ms/notification`;

// Bắt buộc để biết đang test lớp nào
const SECTION_ID = __ENV.SECTION_ID;

const INSTRUCTOR_USER = __ENV.INSTRUCTOR_USER || "instructor";
const INSTRUCTOR_PASS = __ENV.INSTRUCTOR_PASS || "instructor123";
const STUDENT_USER = __ENV.STUDENT_USER || "student";
const STUDENT_PASS = __ENV.STUDENT_PASS || "student123";

function login(username, password) {
  const res = http.post(`${CORE}/auth/login/`, JSON.stringify({ username, password }), {
    headers: { "Content-Type": "application/json" },
  });
  check(res, { "login 200": (r) => r.status === 200 });
  return res.json().data.access;
}

export function setup() {
  if (!SECTION_ID) {
    throw new Error("Missing SECTION_ID. Run with: -e SECTION_ID=<uuid>");
  }

  const instructorToken = login(INSTRUCTOR_USER, INSTRUCTOR_PASS);
  const studentToken = login(STUDENT_USER, STUDENT_PASS);

  // Lấy roster để lấy student_id thật
  const rosterRes = http.get(
    `${CORE}/enrollment/enrollments/by-section?section_id=${SECTION_ID}`,
    { headers: { Authorization: `Bearer ${instructorToken}` } }
  );

  check(rosterRes, { "roster 200": (r) => r.status === 200 });

  const roster = rosterRes.json().data || [];
  const studentIds = roster.map((x) => x.student).slice(0, 10); // tối đa 10 student để payload vừa phải

  if (studentIds.length === 0) {
    throw new Error("Roster is empty. Enroll at least 1 student before running this test.");
  }

  return { instructorToken, studentToken, studentIds };
}

export default function (data) {
  const hInstructor = { headers: { Authorization: `Bearer ${data.instructorToken}` } };
  const hStudent = { headers: { Authorization: `Bearer ${data.studentToken}` } };

  // 1) Read (Instructor)
  const r1 = http.get(`${CORE}/section/sections/`, hInstructor);
  check(r1, { "sections 200": (r) => r.status === 200 });

  const r2 = http.get(`${CORE}/enrollment/enrollments/by-section?section_id=${SECTION_ID}`, hInstructor);
  check(r2, { "roster 200": (r) => r.status === 200 });

  // 2) Write: bulk_enter (Instructor - draft)
  const grades = data.studentIds.map((sid) => ({
    student_id: sid,
    grade_value: Math.floor(Math.random() * 101) / 10, // 0.0..10.0
  }));

  const r3 = http.post(
    `${CORE}/assessment/grades/bulk_enter/`,
    JSON.stringify({ section_id: SECTION_ID, grades }),
    {
      headers: {
        Authorization: `Bearer ${data.instructorToken}`,
        "Content-Type": "application/json",
      },
    }
  );
  check(r3, { "bulk_enter 200": (r) => r.status === 200 });

  // 3) Publish thỉnh thoảng (5%) để tạo event GradePublished (thực tế + không spam)
  if (Math.random() < 0.05) {
    const rPub = http.post(
      `${CORE}/assessment/grades/publish/`,
      JSON.stringify({ section_id: SECTION_ID }),
      {
        headers: {
          Authorization: `Bearer ${data.instructorToken}`,
          "Content-Type": "application/json",
        },
      }
    );
    // chấp nhận 200; nếu hệ thống có rule chống publish liên tục, có thể ra 409/400 -> vẫn coi là "không crash"
    check(rPub, { "publish ok (no 5xx)": (r) => r.status < 500 });
  }

  // 4) Student xem điểm
  const r4 = http.get(`${CORE}/assessment/grades/`, hStudent);
  check(r4, { "student grades 200": (r) => r.status === 200 });

  // 5) Notification đọc messages (kiểm tra service không nghẽn)
  const r5 = http.get(`${NOTI}/messages/`);
  check(r5, { "noti messages 200": (r) => r.status === 200 });

  sleep(0.2);
}
