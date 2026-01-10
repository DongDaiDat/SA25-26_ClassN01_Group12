from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from modules.shared.permissions import role_permission
from modules.shared.exceptions import BusinessRuleViolation
from modules.enrollment.infrastructure.models import Enrollment
from modules.enrollment.application.services import EnrollmentService, EnrollmentOverrideService
from .serializers import EnrollSerializer, EnrollmentSerializer, OverrideEnrollSerializer

class EnrollmentViewSet(viewsets.ViewSet):
    def list(self, request):
        if request.user.role in ("ADMIN","REGISTRAR","MANAGER"):
            qs = Enrollment.objects.all().order_by("-created_at")[:200]
        else:
            qs = Enrollment.objects.filter(student=request.user).order_by("-created_at")
        return Response(EnrollmentSerializer(qs, many=True).data)

    def create(self, request):
        if request.user.role != "STUDENT":
            return Response({"error":{"code":"FORBIDDEN","message":"Only students can enroll","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        ser = EnrollSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        idem = request.headers.get("Idempotency-Key")
        if not idem:
            raise BusinessRuleViolation("IDEMPOTENCY_REQUIRED", "Idempotency-Key header is required", status_code=400)
        res = EnrollmentService.enroll(student=request.user, section_id=str(ser.validated_data["section_id"]), idempotency_key=idem, correlation_id=getattr(request,"request_id",""))
        return Response(res, status=201)

    def destroy(self, request, pk=None):
        if request.user.role != "STUDENT":
            return Response({"error":{"code":"FORBIDDEN","message":"Only students can cancel their enrollment","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        res = EnrollmentService.cancel(student=request.user, enrollment_id=pk, correlation_id=getattr(request,"request_id",""))
        return Response(res)

    @action(detail=False, methods=["post"])
    def override(self, request):
        if request.user.role not in ("ADMIN","REGISTRAR"):
            return Response({"error":{"code":"FORBIDDEN","message":"Only registrar can override","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        ser = OverrideEnrollSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        idem = request.headers.get("Idempotency-Key")
        if not idem:
            raise BusinessRuleViolation("IDEMPOTENCY_REQUIRED", "Idempotency-Key header is required", status_code=400)
        res = EnrollmentOverrideService.override_enroll(
            approver=request.user,
            student_id=str(ser.validated_data["student_id"]),
            section_id=str(ser.validated_data["section_id"]),
            reason=ser.validated_data["reason"],
            idempotency_key=idem,
            correlation_id=getattr(request,"request_id",""),
        )
        return Response(res, status=201)
