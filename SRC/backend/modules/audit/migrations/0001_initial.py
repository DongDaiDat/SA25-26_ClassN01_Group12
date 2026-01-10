from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("identity_access","0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(max_length=120)),
                ("entity_type", models.CharField(max_length=120, blank=True, default="")),
                ("entity_id", models.CharField(max_length=64, blank=True, default="")),
                ("result", models.CharField(max_length=20, default="SUCCESS")),
                ("reason_code", models.CharField(max_length=80, blank=True, default="")),
                ("before", models.JSONField(null=True, blank=True)),
                ("after", models.JSONField(null=True, blank=True)),
                ("correlation_id", models.CharField(max_length=100, blank=True, default="")),
                ("ip", models.GenericIPAddressField(null=True, blank=True)),
                ("user_agent", models.CharField(max_length=255, blank=True, default="")),
                ("actor", models.ForeignKey(null=True, blank=True, to="identity_access.user", on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs")),
            ],
            options={"indexes":[
                models.Index(fields=["action","created_at"], name="audit_action_time"),
                models.Index(fields=["entity_type","entity_id"], name="audit_entity"),
            ]},
        ),
    ]
