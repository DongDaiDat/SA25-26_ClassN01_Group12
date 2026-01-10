from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from modules.shared.permissions import role_permission
from modules.program.infrastructure.models import Program, CurriculumVersion, CurriculumNode, CurriculumRule
from modules.program.application.services import CurriculumService
from .serializers import ProgramSerializer, CurriculumVersionSerializer, CurriculumNodeSerializer, CurriculumRuleSerializer

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by("code")
    serializer_class = ProgramSerializer
    filterset_fields = ["status"]
    search_fields = ["code","name"]
    ordering_fields = ["code","name","created_at"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
        return [role_permission("ADMIN","REGISTRAR")()]

class CurriculumVersionViewSet(viewsets.ModelViewSet):
    queryset = CurriculumVersion.objects.select_related("program").all().order_by("-effective_year","version_code")
    serializer_class = CurriculumVersionSerializer
    filterset_fields = ["program","status","effective_year"]
    search_fields = ["version_code","program__code"]
    ordering_fields = ["effective_year","version_code","created_at"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
        return [role_permission("ADMIN","REGISTRAR")()]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        cv = CurriculumService.publish(pk, actor=request.user, correlation_id=getattr(request,"request_id", ""))
        return Response(self.get_serializer(cv).data)

class CurriculumNodeViewSet(viewsets.ModelViewSet):
    queryset = CurriculumNode.objects.all().order_by("sort_order","title")
    serializer_class = CurriculumNodeSerializer
    filterset_fields = ["curriculum","node_type"]
    search_fields = ["title"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
        return [role_permission("ADMIN","REGISTRAR")()]

class CurriculumRuleViewSet(viewsets.ModelViewSet):
    queryset = CurriculumRule.objects.all().order_by("-created_at")
    serializer_class = CurriculumRuleSerializer
    filterset_fields = ["node","rule_type"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
        return [role_permission("ADMIN","REGISTRAR")()]
