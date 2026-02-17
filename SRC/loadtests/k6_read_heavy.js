import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "20s", target: 10 },  // tăng lên 10 user ảo
    { duration: "40s", target: 60 },  // giữ 30
    { duration: "40s", target: 150 },  // tăng lên 60
    { duration: "20s", target: 0 },   // giảm về 0
  ],
  thresholds: {
    http_req_failed: ["rate<0.02"],     // lỗi < 2%
    http_req_duration: ["p(95)<1000"],  // p95 < 1000ms (máy local docker)
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const CORE = `${BASE}/api/v1`;
const NOTI = `${BASE}/ms/notification`;

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
  const instructorToken = login(INSTRUCTOR_USER, INSTRUCTOR_PASS);
  const studentToken = login(STUDENT_USER, STUDENT_PASS);
  return { instructorToken, studentToken };
}

export default function (data) {
  // Instructor: đọc sections
  const h1 = { headers: { Authorization: `Bearer ${data.instructorToken}` } };
  const r1 = http.get(`${CORE}/section/sections/`, h1);
  check(r1, { "sections 200": (r) => r.status === 200 });

  // Student: đọc grades
  const h2 = { headers: { Authorization: `Bearer ${data.studentToken}` } };
  const r2 = http.get(`${CORE}/assessment/grades/`, h2);
  check(r2, { "grades 200": (r) => r.status === 200 });

  // Notification: đọc messages
  const r3 = http.get(`${NOTI}/messages/`);
  check(r3, { "noti messages 200": (r) => r.status === 200 });

  sleep(0.2);
}
