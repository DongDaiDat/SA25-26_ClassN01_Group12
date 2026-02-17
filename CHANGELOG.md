# Changelog

(Trọng tâm: những gì *thể hiện trong mã nguồn hiện tại* + các artefact đi kèm trong repo.)

---

## Lab 1 – Thu thập & Mô hình hóa Yêu cầu

**Added**
- Khung thư mục tài liệu phục vụ giai đoạn yêu cầu: `Documents/` (Plan, SRS, WeeklyReports, báo cáo tổng hợp).
- Báo cáo/artefact Lab 1 trong `Documents/WeeklyReports/` (Requirements Elicitation & Use Case Modeling).

**Notes**
- Lab 1 chủ yếu là tài liệu hóa/mô hình hóa, chưa yêu cầu lập trình.

---

## Lab 2 – Thiết kế kiến trúc Phân lớp (Logical View)

**Added**
- Quy ước kiến trúc **layered** theo module/bounded-context trong monolith:
  - `presentation/` (API: views/serializers/urls)
  - `application/` (use-cases/services)
  - `domain/` (domain objects / rules)
  - `infrastructure/` (ORM models/repos)
  - `shared/` (cross-cutting concerns)
- Chuẩn hóa “cross-cutting concerns”:
  - Correlation/Trace ID (`RequestIDMiddleware`) + propagate qua header `X-Request-Id`.
  - JSON response envelope + custom exception handler (`modules.shared.api`).
  - Permission/RBAC helpers (`modules.shared.permissions`).

**Changed**
- Tập trung hóa cấu hình Django/DRF theo `config/` (settings, urls, celery).

---

## Lab 3 – Triển khai kiến trúc phân lớp (Chức năng CRUD)

**Added**
- Scaffold backend **Django + DRF** (monolith) trong `SRC/backend/`:
  - OpenAPI schema + Swagger UI: `/api/schema/`, `/api/docs/`.
  - Health endpoint: `/api/health`.
- Các module nghiệp vụ (CRUD/flows) theo bounded context trong `SRC/backend/modules/`:
  - `identity_access`: User + JWT auth (login/refresh/logout) + RBAC.
  - `program`: CRUD chương trình đào tạo.
  - `course_catalog`: CRUD course + quản lý prerequisites.
  - `term_scheduling`: term + enrollment window/lock.
  - `class_section`: CRUD section + schedule/quota.
  - `enrollment`: enroll/cancel + rule checks + idempotency.
  - `assessment`: grade entry/publish/view.
  - `certificate`: định nghĩa chứng chỉ + issue/verify.
  - `audit`: ghi audit log.
- Seed dữ liệu demo (management commands) để chạy nhanh flow end-to-end.

**Fixed**
- Tăng độ an toàn khi generate schema (AnonymousUser có `role` để tránh crash khi check RBAC).

---

## Lab 4 – Phân tách Microservice & Thiết kế Giao tiếp

**Added**
- Thiết kế theo hướng **microservices principles** nhưng triển khai theo **Modular Monolith + 1 microservice**:
  - Mỗi domain là 1 Django app độc lập trong `modules/` (rõ ràng boundary, ownership).
- Quy ước hạn chế phụ thuộc chéo module:
  - Nhiều entity tham chiếu chéo bằng `*_id` (UUID) thay vì FK ORM.
  - Cross-module interaction thông qua application services / domain events (tránh query/join ORM chéo module).

**Notes**
- Đây là bước “design boundary + contracts”; nền tảng để tách Notification service và triển khai EDA ở các lab sau.

---

## Lab 5 – Triển khai Microservice (Dịch vụ Notification)

**Added**
- Microservice `services/notification/` (Django/DRF) chạy độc lập:
  - DB riêng (trong compose: `postgres_notification`).
  - API path namespace: `/ms/notification/...` (health/schema/docs/messages).
- Notification domain:
  - Lưu lịch sử gửi thông báo: `NotificationMessage` (idempotent theo `event_id`).
  - Celery task consumer: `notification.tasks.handle_event`.
  - Provider mock (giả lập gửi EMAIL/SMS) để demo.

---

## Lab 6 – Triển khai API Gateway

**Added**
- Reverse proxy gateway bằng **Nginx** trong `SRC/infra/nginx/nginx.conf`:
  - `/api/` → backend monolith
  - `/ms/notification/` → notification service
  - `/` → frontend
- Docker compose cho DEV/PROD trong `SRC/infra/docker/`:
  - Full stack: `postgres_core`, `postgres_notification`, `rabbitmq`, `backend`, `notification`, `frontend`, `nginx`.
  - Healthcheck + restart policy (prod).

**Notes**
- Gateway hiện đóng vai trò “single entry” và routing; auth/authorization chủ yếu xử lý ở backend monolith (JWT/RBAC).

---

## Lab 7 – Tích hợp bất đồng bộ với Kiến trúc hướng Sự kiện (EDA)

**Added**
- Message broker: **RabbitMQ** (compose) + **Celery** (backend + notification).
- **Outbox Pattern** tại backend monolith:
  - `modules.shared.models.OutboxEvent`
  - Celery beat schedule publish đều đặn (`modules.shared.tasks.publish_outbox`)
  - Publish qua Celery task name cấu hình bằng env: `NOTIFICATION_CELERY_TASK`
- Event catalog (đã “wire” vào Outbox → broker → consumer):
  - `EnrollmentCreated`, `EnrollmentCancelled` (enrollment)
  - `GradePublished` (assessment)
  - `CertificateIssued` (certificate)
- Idempotency & reliability:
  - Enrollment idempotency qua `EnrollmentAttempt.idempotency_key`.
  - Notification consumer ignore duplicate bằng unique `event_id`.

---

## Lab 8 – Sơ đồ triển khai & Phân tích thuộc tính chất lượng (ATAM)

**Added**
- Artefact phục vụ deployment view:
  - Dockerfiles cho `backend/`, `frontend/`, `services/notification/`.
  - Compose DEV/PROD (tách môi trường; `config.settings.dev` vs `config.settings.prod`).
  - Nginx security headers baseline.
- Chuẩn bị kiểm thử chất lượng (phục vụ các kịch bản ATAM về performance/scalability):
  - Load tests: `SRC/loadtests/` (k6 scripts).
  - E2E tests: `SRC/frontend/e2e/` (Playwright).

**Notes**
- Các quyết định triển khai (monolith + notification + EDA) giúp giảm coupling cho tác vụ gửi thông báo, đồng thời giữ hệ thống dễ triển khai ở giai đoạn MVP; k6/e2e hỗ trợ chứng minh các quality scenarios trong ATAM.

---