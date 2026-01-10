from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = [("shared","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Term",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("enroll_open_at", models.DateTimeField()),
                ("enroll_close_at", models.DateTimeField()),
                ("status", models.CharField(max_length=20, default="DRAFT")),
            ],
        ),
    ]
