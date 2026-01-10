from django.contrib.auth import get_user_model

User = get_user_model()

def ensure_seed_users():
    seeds = [
        ("admin", "admin123", User.ROLE_ADMIN),
        ("registrar", "registrar123", User.ROLE_REGISTRAR),
        ("instructor", "instructor123", User.ROLE_INSTRUCTOR),
        ("student", "student123", User.ROLE_STUDENT),
    ]
    created = []
    for username, password, role in seeds:
        u, was_created = User.objects.get_or_create(username=username, defaults={"role": role, "email": f"{username}@example.com"})
        if was_created:
            u.set_password(password)
            u.save()
        else:
            # keep password stable for dev convenience
            if not u.check_password(password):
                u.set_password(password)
                u.save()
            if u.role != role:
                u.role = role
                u.save(update_fields=["role"])
        created.append(username)
    return created
