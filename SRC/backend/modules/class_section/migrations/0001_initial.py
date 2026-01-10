from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("identity_access","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("term_id", models.UUIDField()),
                ("course_id", models.UUIDField()),
                ("section_code", models.CharField(max_length=20)),
                ("capacity", models.IntegerField()),
                ("enrolled_count", models.IntegerField(default=0)),
                ("status", models.CharField(max_length=20, default="ACTIVE")),
            ],
            options={"unique_together": {("term_id","course_id","section_code")}, "indexes":[models.Index(fields=["term_id","course_id"], name="section_term_course")]},
        ),
        migrations.CreateModel(
            name="SectionInstructor",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("instructor", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="teaching_sections")),
                ("section", models.ForeignKey(to="class_section.section", on_delete=django.db.models.deletion.CASCADE, related_name="instructors")),
            ],
            options={"unique_together": {("section","instructor")}},
        ),
        migrations.CreateModel(
            name="ScheduleSlot",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("day_of_week", models.IntegerField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("room", models.ForeignKey(null=True, blank=True, to="class_section.room", on_delete=django.db.models.deletion.SET_NULL)),
                ("section", models.ForeignKey(to="class_section.section", on_delete=django.db.models.deletion.CASCADE, related_name="schedule_slots")),
            ],
            options={"indexes":[models.Index(fields=["section","day_of_week"], name="slot_section_day")]},
        ),
    ]
