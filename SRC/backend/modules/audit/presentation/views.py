from rest_framework import viewsets
from modules.shared.permissions import role_permission
from modules.audit.infrastructure.models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by("-created_at")
    serializer_class = AuditLogSerializer
    filterset_fields = ["action","result","entity_type"]
    search_fields = ["entity_id","reason_code","actor__username"]
    ordering_fields = ["created_at","action","entity_type"]

    def get_permissions(self):
        return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
