from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("shared","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Program",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("status", models.CharField(max_length=20, default="ACTIVE")),
            ],
        ),
        migrations.CreateModel(
            name="CurriculumVersion",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("version_code", models.CharField(max_length=20)),
                ("status", models.CharField(max_length=20, default="DRAFT")),
                ("effective_year", models.IntegerField()),
                ("notes", models.TextField(blank=True, default="")),
                ("program", models.ForeignKey(to="program.program", on_delete=django.db.models.deletion.PROTECT, related_name="curricula")),
            ],
            options={"unique_together": {("program","version_code")}},
        ),
        migrations.CreateModel(
            name="CurriculumNode",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("node_type", models.CharField(max_length=30, default="GROUP")),
                ("title", models.CharField(max_length=255)),
                ("sort_order", models.IntegerField(default=0)),
                ("curriculum", models.ForeignKey(to="program.curriculumversion", on_delete=django.db.models.deletion.CASCADE, related_name="nodes")),
                ("parent", models.ForeignKey(to="program.curriculumnode", null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name="children")),
            ],
        ),
        migrations.CreateModel(
            name="CurriculumRule",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("rule_type", models.CharField(max_length=50)),
                ("params", models.JSONField(default=dict)),
                ("node", models.ForeignKey(to="program.curriculumnode", on_delete=django.db.models.deletion.CASCADE, related_name="rules")),
            ],
        ),
    ]
