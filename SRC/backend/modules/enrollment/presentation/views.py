from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from modules.shared.exceptions import BusinessRuleViolation
from modules.enrollment.infrastructure.models import Enrollment
from modules.enrollment.application.services import EnrollmentService, EnrollmentOverrideService
from modules.class_section.application.services import SectionQueryService as SQ
from .serializers import EnrollSerializer, EnrollmentSerializer, OverrideEnrollSerializer


class EnrollmentViewSet(viewsets.ViewSet):
    def list(self, request):
        if request.user.role in ("ADMIN", "REGISTRAR", "MANAGER"):
            qs = Enrollment.objects.all().order_by("-created_at")[:200]
        else:
            qs = Enrollment.objects.filter(student=request.user).order_by("-created_at")
        return Response(EnrollmentSerializer(qs, many=True).data)

    def create(self, request):
        if request.user.role != "STUDENT":
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Only students can enroll", "details": {}, "trace_id": getattr(request, "request_id", None)}},
                status=403,
            )
        ser = EnrollSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        idem = request.headers.get("Idempotency-Key")
        if not idem:
            raise BusinessRuleViolation("IDEMPOTENCY_REQUIRED", "Idempotency-Key header is required", status_code=400)

        res = EnrollmentService.enroll(
            student=request.user,
            section_id=str(ser.validated_data["section_id"]),
            idempotency_key=idem,
            correlation_id=getattr(request, "request_id", ""),
        )
        return Response(res, status=201)

    def destroy(self, request, pk=None):
        if request.user.role != "STUDENT":
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Only students can cancel their enrollment", "details": {}, "trace_id": getattr(request, "request_id", None)}},
                status=403,
            )
        res = EnrollmentService.cancel(student=request.user, enrollment_id=pk, correlation_id=getattr(request, "request_id", ""))
        return Response(res)

    @action(detail=False, methods=["post"])
    def override(self, request):
        if request.user.role not in ("ADMIN", "REGISTRAR"):
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Only registrar can override", "details": {}, "trace_id": getattr(request, "request_id", None)}},
                status=403,
            )
        ser = OverrideEnrollSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        idem = request.headers.get("Idempotency-Key")
        if not idem:
            raise BusinessRuleViolation("IDEMPOTENCY_REQUIRED", "Idempotency-Key header is required", status_code=400)

        # student_id is int (serializer)
        res = EnrollmentOverrideService.override_enroll(
            approver=request.user,
            student_id=ser.validated_data["student_id"],
            section_id=str(ser.validated_data["section_id"]),
            reason=ser.validated_data["reason"],
            idempotency_key=idem,
            correlation_id=getattr(request, "request_id", ""),
        )
        return Response(res, status=201)

    # ✅ roster theo section_id (endpoint chuẩn)
    @action(detail=False, methods=["get"], url_path="by-section")
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return Response({"detail": "section_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        role = getattr(request.user, "role", None)
        if role not in ("ADMIN", "REGISTRAR", "MANAGER", "INSTRUCTOR"):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        # security: INSTRUCTOR chỉ xem section của mình
        if role == "INSTRUCTOR" and not SQ.is_instructor_of_section(str(request.user.id), str(section_id)):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        qs = Enrollment.objects.filter(section_id=section_id, status="ACTIVE").order_by("student_id")
        return Response(EnrollmentSerializer(qs, many=True).data)

    # ✅ alias endpoint cũ: by_section
    @action(detail=False, methods=["get"], url_path="by_section")
    def by_section_alias(self, request):
        return self.by_section(request)
