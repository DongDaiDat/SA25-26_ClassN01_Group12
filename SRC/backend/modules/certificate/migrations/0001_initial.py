from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("identity_access","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="CertificateDefinition",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                ("rules", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="CertificateIssue",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("verify_code", models.CharField(max_length=20, unique=True)),
                ("status", models.CharField(max_length=20, default="ISSUED")),
                ("metadata", models.JSONField(default=dict)),
                ("definition", models.ForeignKey(to="certificate.certificatedefinition", on_delete=django.db.models.deletion.PROTECT, related_name="issues")),
                ("issued_by", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="issued_certificates")),
                ("student", models.ForeignKey(to="identity_access.user", on_delete=django.db.models.deletion.PROTECT, related_name="certificates")),
            ],
        ),
    ]
