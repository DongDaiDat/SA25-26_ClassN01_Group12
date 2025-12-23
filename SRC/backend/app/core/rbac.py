from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    TRAINING_OFFICE = "TRAINING_OFFICE"
    FACULTY = "FACULTY"
    QA = "QA"
    DEPT_HEAD = "DEPT_HEAD"
    LECTURER = "LECTURER"
    VIEWER = "VIEWER"
    SIS_STAFF = "SIS_STAFF"

PERM = {
    "PROGRAM_VIEW": {Role.ADMIN, Role.TRAINING_OFFICE, Role.FACULTY, Role.QA, Role.DEPT_HEAD, Role.LECTURER, Role.VIEWER},
    "PROGRAM_CREATE": {Role.ADMIN, Role.TRAINING_OFFICE},
    "COURSE_MANAGE": {Role.ADMIN, Role.TRAINING_OFFICE},
    "SYLLABUS_EDIT": {Role.ADMIN, Role.LECTURER, Role.DEPT_HEAD},
    "WORKFLOW_APPROVE": {Role.ADMIN, Role.TRAINING_OFFICE, Role.FACULTY, Role.QA, Role.DEPT_HEAD},
    "REPORT_EXPORT": {Role.ADMIN, Role.TRAINING_OFFICE, Role.QA},
    "SIS_MANAGE": {Role.ADMIN, Role.SIS_STAFF, Role.TRAINING_OFFICE},
    "AUDIT_VIEW": {Role.ADMIN, Role.QA},
}

# Bloom: lưu int 1..6 (chuẩn), hiển thị VI/EN theo map
BLOOM = {
    1: {"en": "Remember", "vi": "Ghi nhớ"},
    2: {"en": "Understand", "vi": "Hiểu"},
    3: {"en": "Apply", "vi": "Vận dụng"},
    4: {"en": "Analyze", "vi": "Phân tích"},
    5: {"en": "Evaluate", "vi": "Đánh giá"},
    6: {"en": "Create", "vi": "Sáng tạo"},
}
