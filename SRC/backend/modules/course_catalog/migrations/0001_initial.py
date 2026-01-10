from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("shared","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("credits", models.IntegerField()),
                ("status", models.CharField(max_length=20, default="ACTIVE")),
                ("description", models.TextField(blank=True, default="")),
            ],
            options={"indexes":[models.Index(fields=["code"], name="course_code_idx")]},
        ),
        migrations.CreateModel(
            name="CoursePrerequisite",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("min_grade", models.FloatField(null=True, blank=True)),
                ("course", models.ForeignKey(to="course_catalog.course", on_delete=django.db.models.deletion.CASCADE, related_name="prerequisites")),
                ("prereq_course", models.ForeignKey(to="course_catalog.course", on_delete=django.db.models.deletion.PROTECT, related_name="required_for")),
            ],
            options={"unique_together": {("course","prereq_course")}},
        ),
    ]
