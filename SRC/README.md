# TPMS – Training Program Management System (Modular Monolith + Notification Microservice)

Kiến trúc **Modular Monolith (Django/DRF)** + **Microservice Notification (Django/DRF)**, dùng **RabbitMQ + Celery** để publish/consume event (Outbox pattern).

## 1) Repo structure

```
/
  backend/
    config/
    modules/
      identity_access/
      program/
      course_catalog/
      term_scheduling/
      class_section/
      enrollment/
      assessment/
      certificate/
      audit/
      shared/
  services/
    notification/
      app/
  frontend/
  infra/
    nginx/
    docker/
  .github/workflows/ci.yml
  README.md
```

## 2) Quick start (DEV)

### 2.1 Env
```bash
cd infra/docker
cp .env.example .env
```

### 2.2 Run
```bash
docker compose -f docker-compose.dev.yml --env-file .env up --build -d
```

### 2.3 Migrate + seed
Monolith:
```bash
docker compose -f infra/docker/docker-compose.dev.yml exec backend python manage.py migrate
docker compose -f infra/docker/docker-compose.dev.yml exec backend python manage.py seed_data
docker compose -f infra/docker/docker-compose.dev.yml exec backend python manage.py seed_demo
```

Notification service:
```bash
docker compose -f infra/docker/docker-compose.dev.yml exec notification python manage.py migrate
```

## 3) URLs

- Gateway (Nginx): http://localhost
- Frontend: http://localhost
- Swagger (monolith): http://localhost/api/docs
- Schema (monolith): http://localhost/api/schema
- Health (monolith): http://localhost/api/health
- Notification health: http://localhost/ms/notification/health
- Notification docs: http://localhost/ms/notification/docs

RabbitMQ management: http://localhost:15672 (guest/guest)

## 4) Auth & RBAC

JWT Access/Refresh (SimpleJWT, rotate + blacklist).

Roles:
- `ADMIN`
- `REGISTRAR` (Giáo vụ)
- `INSTRUCTOR`
- `STUDENT`
- `MANAGER` (optional)

Seed accounts (DEV):
- admin / admin123
- registrar / registrar123
- instructor / instructor123
- student / student123

Core endpoints:
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `POST /api/v1/auth/logout/`
- `GET  /api/v1/auth/whoami/`

## 5) Demo flows (End-to-end)

### Flow 1: Student enroll -> Outbox -> RabbitMQ -> Notification history
1. Login bằng `student/student123`
2. Vào **Enrollment** → enroll 1 section
3. Backend tạo Enrollment + ghi **OutboxEvent (EnrollmentCreated)**
4. Celery Beat (backend_beat) chạy `publish_outbox` → push Celery task sang **Notification worker**
5. Notification service consume → lưu `NotificationMessage`
6. Vào **Notifications** (frontend) → thấy lịch sử

### Flow 2: Instructor nhập điểm -> Student xem điểm
1. Login bằng `instructor/instructor123`
2. Vào **Grade Entry** → chọn section → nhập grade (student UUID) → Save Draft → Publish
3. Login lại bằng `student/student123` → **Grades** để xem grade

### Flow 3: Issue certificate -> verify by code
1. Login bằng `registrar/registrar123`
2. Tạo certificate definition (rules: required_course_ids + min_grade)
3. Issue cho student (student UUID)
4. Verify: nhập verify code → gọi `GET /api/v1/certificate/issues/verify/?code=...`

## 6) Event catalog (implemented)

### EnrollmentCreated (v1)
- OutboxEvent.event_type: `EnrollmentCreated`
- Payload (monolith):
```json
{
  "student_id": "uuid",
  "section_id": "uuid",
  "term_id": "uuid",
  "course_id": "uuid",
  "source": "NORMAL|OVERRIDE"
}
```

Delivery:
- Monolith Outbox → Celery Beat `modules.shared.tasks.publish_outbox` → Celery task name: `notification.tasks.handle_event`
- Notification service creates `NotificationMessage` with `event_id` unique (idempotent).

## 7) Architecture rules (Modular Monolith)

- Mỗi bounded context = 1 Django app trong `backend/modules/`
- Layer:
  - `presentation/` (views/serializers/urls)
  - `application/` (use-cases)
  - `domain/` (domain objects/events)
  - `infrastructure/` (ORM models/repos)
- **Không join/query chéo module bằng ORM**: các module dùng `*_id` (UUID) để tham chiếu; cross-module thông qua Application Services hoặc Domain Events.

## 8) Traceability matrix (FR → Module → Endpoint → Entities → Events → Tests)

| FR | Module | Endpoint(s) | Entities | Event | Tests |
|---|---|---|---|---|---|
| Auth login/refresh/logout + RBAC | identity_access | /auth/login /auth/refresh /auth/logout /auth/whoami | User, RefreshTokenBlacklist | - | - |
| CRUD Program | program | /program/programs | Program | - | - |
| CRUD Course + Prereq | course_catalog | /course-catalog/courses, /courses/{id}/prerequisites | Course, CoursePrerequisite | - | `test_course_prereq.py` |
| Term + window + lock | term_scheduling | /term/terms, /terms/{id}/status | Term | - | - |
| CRUD Section + schedule + quota | class_section | /section/sections, /sections/{id}/schedule | Section, ScheduleSlot | - | - |
| Enroll/Cancel + rule check | enrollment | /enrollment/enrollments | Enrollment, EnrollmentAttempt | EnrollmentCreated | `test_enrollment_service.py` |
| Grade entry/publish/view | assessment | /assessment/grades/bulk_enter, /publish, /grades | GradeRecord, SectionGradePolicy | GradePublished (optional) | - |
| Certificate issue/verify | certificate | /certificate/definitions, /issues/issue, /issues/verify | CertificateDefinition, CertificateIssue | CertificateIssued (optional) | - |
| Audit log | audit | /audit/logs | AuditLog | - | - |
| Notification history | notification service | /ms/notification/messages | NotificationMessage | consume EnrollmentCreated | - |

## 9) Notes / Assumptions (GIẢ ĐỊNH)

- `Section` lưu `term_id`, `course_id` (UUID) thay vì FK để tuân thủ “không query chéo module”.
- Pass grade: **>= 5.0/10**.
- Notification API hiện **chưa áp auth** (chỉ để demo dev). Production nên thêm auth/JWT & RBAC.
- Certificate rule đơn giản: `required_course_ids[]` + `min_grade`. Chưa triển khai tính credits theo program.

## 10) Questions (để hoàn thiện >90%)

1. Thang điểm & rule pass thực tế: 0-10 hay chữ (A/B/C), có đổi thang?
2. Certificate điều kiện theo **Program completion** (credits, bắt buộc môn, GPA) cụ thể như nào?
3. Enrollment rule chi tiết:
   - có allow “repeat course” không?
   - có waitlist không?
4. Notification kênh thật: Email/SMS provider nào? Template chuẩn?
