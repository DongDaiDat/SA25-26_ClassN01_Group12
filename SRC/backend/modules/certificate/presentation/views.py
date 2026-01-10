from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from modules.shared.permissions import role_permission
from modules.certificate.infrastructure.models import CertificateDefinition, CertificateIssue
from modules.certificate.application.services import CertificateService
from .serializers import CertificateDefinitionSerializer, CertificateIssueSerializer, IssueRequestSerializer

class CertificateDefinitionViewSet(viewsets.ModelViewSet):
    queryset = CertificateDefinition.objects.all().order_by("code")
    serializer_class = CertificateDefinitionSerializer
    search_fields = ["code","name"]
    filterset_fields = ["code"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER","INSTRUCTOR","STUDENT")()]
        return [role_permission("ADMIN","REGISTRAR")()]

class CertificateIssueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CertificateIssue.objects.select_related("definition","student").all().order_by("-created_at")
    serializer_class = CertificateIssueSerializer
    filterset_fields = ["status","definition"]
    search_fields = ["verify_code","student__username","definition__code"]

    def get_permissions(self):
        if self.action in ("verify",):
            return [AllowAny()]
        if self.action in ("list","retrieve"):
            if self.request.user.role in ("STUDENT",):
                return [role_permission("STUDENT")()]
            return [role_permission("ADMIN","REGISTRAR","MANAGER")()]
        return [role_permission("ADMIN","REGISTRAR")()]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request,"user",None) and self.request.user.is_authenticated and self.request.user.role == "STUDENT":
            return qs.filter(student=self.request.user)
        return qs

    @action(detail=False, methods=["post"])
    def issue(self, request):
        if request.user.role not in ("ADMIN","REGISTRAR"):
            return Response({"error":{"code":"FORBIDDEN","message":"Only registrar can issue certificates","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        ser = IssueRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        issue = CertificateService.issue(actor=request.user, definition_id=str(ser.validated_data["definition_id"]),
                                         student_id=str(ser.validated_data["student_id"]), correlation_id=getattr(request,"request_id",""))
        return Response(CertificateIssueSerializer(issue).data, status=201)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def verify(self, request):
        code = request.query_params.get("code","").strip()
        obj = CertificateIssue.objects.select_related("definition","student").filter(verify_code=code, status="ISSUED").first()
        if not obj:
            return Response({"valid": False}, status=200)
        return Response({"valid": True, "definition": obj.definition.code, "student": obj.student.username, "issued_at": obj.created_at.isoformat()}, status=200)
