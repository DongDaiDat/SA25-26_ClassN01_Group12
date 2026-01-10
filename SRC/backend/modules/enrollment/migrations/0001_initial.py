from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("identity_access","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section_id", models.UUIDField()),
                ("term_id", models.UUIDField()),
                ("course_id", models.UUIDField()),
                ("status", models.CharField(max_length=20, default="ACTIVE")),
                ("source", models.CharField(max_length=20, default="NORMAL")),
                ("reason", models.CharField(max_length=255, blank=True, default="")),
                ("canceled_at", models.DateTimeField(null=True, blank=True)),
                ("student", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="enrollments")),
            ],
            options={"unique_together": {("student","section_id")}, "indexes":[
                models.Index(fields=["student","status"], name="enr_student_status"),
                models.Index(fields=["term_id"], name="enr_term_idx"),
            ]},
        ),
        migrations.CreateModel(
            name="EnrollmentAttempt",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("idempotency_key", models.CharField(max_length=80, unique=True)),
                ("section_id", models.UUIDField()),
                ("result", models.JSONField(default=dict)),
                ("student", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name="OverrideDecision",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section_id", models.UUIDField()),
                ("bypass_flags", models.JSONField(default=dict)),
                ("reason", models.CharField(max_length=255)),
                ("approver", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="approved_overrides")),
                ("student", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="override_decisions")),
            ],
        ),
    ]
