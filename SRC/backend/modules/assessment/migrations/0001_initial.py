from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("identity_access","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="SectionGradePolicy",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section_id", models.UUIDField(unique=True)),
                ("grading_status", models.CharField(max_length=20, default="OPEN")),
                ("publish_status", models.CharField(max_length=20, default="HIDDEN")),
            ],
        ),
        migrations.CreateModel(
            name="GradeRecord",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section_id", models.UUIDField()),
                ("term_id", models.UUIDField()),
                ("course_id", models.UUIDField()),
                ("grade_value", models.FloatField(null=True, blank=True)),
                ("grade_scale", models.CharField(max_length=20, default="0-10")),
                ("status", models.CharField(max_length=20, default="DRAFT")),
                ("student", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="grades")),
                ("updated_by", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="grade_updates")),
            ],
            options={"unique_together": {("student","section_id")}, "indexes":[models.Index(fields=["student","course_id","status"], name="grade_student_course")]},
        ),
        migrations.CreateModel(
            name="GradeChangeLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("old_value", models.FloatField(null=True, blank=True)),
                ("new_value", models.FloatField(null=True, blank=True)),
                ("reason", models.CharField(max_length=255)),
                ("changed_by", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT)),
                ("grade_record", models.ForeignKey(to="assessment.graderecord", on_delete=django.db.models.deletion.CASCADE, related_name="changes")),
            ],
        ),
    ]
