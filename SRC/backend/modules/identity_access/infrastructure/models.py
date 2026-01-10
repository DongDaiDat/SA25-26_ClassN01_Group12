from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_REGISTRAR = "REGISTRAR"
    ROLE_INSTRUCTOR = "INSTRUCTOR"
    ROLE_STUDENT = "STUDENT"
    ROLE_MANAGER = "MANAGER"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_REGISTRAR, "Registrar"),
        (ROLE_INSTRUCTOR, "Instructor"),
        (ROLE_STUDENT, "Student"),
        (ROLE_MANAGER, "Manager"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    def __str__(self):
        return f"{self.username}({self.role})"
