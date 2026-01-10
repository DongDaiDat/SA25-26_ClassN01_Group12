from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="NotificationMessage",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_id", models.UUIDField(unique=True, null=True, blank=True)),
                ("event_type", models.CharField(max_length=120, blank=True, default="")),
                ("channel", models.CharField(max_length=20, default="EMAIL")),
                ("to", models.CharField(max_length=255)),
                ("subject", models.CharField(max_length=255, blank=True, default="")),
                ("body", models.TextField(blank=True, default="")),
                ("status", models.CharField(max_length=20, default="SENT")),
                ("provider_response", models.JSONField(default=dict)),
                ("retry_count", models.IntegerField(default=0)),
                ("correlation_id", models.CharField(max_length=100, blank=True, default="")),
            ],
            options={"indexes":[models.Index(fields=["event_type","created_at"], name="notif_evt_time")]},
        ),
    ]
