ROLE_PERMISSIONS = {
    "ADMIN": {"*"},
    "REGISTRAR": {
        "program.manage","course.manage","term.manage","section.manage",
        "enrollment.override","audit.view","certificate.manage","report.view"
    },
    "INSTRUCTOR": {"grade.manage","roster.view","grade.publish"},
    "STUDENT": {"enrollment.self","grade.view.self","certificate.lookup"},
    "MANAGER": {"report.view","audit.view"},
}

def has_permission(role: str, perm: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, set())
    return "*" in perms or perm in perms
