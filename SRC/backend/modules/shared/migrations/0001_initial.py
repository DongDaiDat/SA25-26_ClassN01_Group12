from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="OutboxEvent",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(max_length=20, default="NEW")),
                ("event_type", models.CharField(max_length=100)),
                ("version", models.IntegerField(default=1)),
                ("correlation_id", models.CharField(max_length=100, blank=True, default="")),
                ("payload", models.JSONField()),
                ("published_at", models.DateTimeField(null=True, blank=True)),
                ("retry_count", models.IntegerField(default=0)),
            ],
            options={
                "indexes":[models.Index(fields=["status","event_type","created_at"], name="outbox_status_evt")]
            },
        ),
    ]
