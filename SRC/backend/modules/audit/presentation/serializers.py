from rest_framework import serializers
from modules.audit.infrastructure.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id","created_at","actor_username","action","entity_type","entity_id","result","reason_code","before","after","correlation_id","ip","user_agent"]
        read_only_fields = fields
