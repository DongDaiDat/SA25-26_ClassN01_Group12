from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from modules.assessment.infrastructure.models import GradeRecord
from modules.assessment.application.services import GradeEntryService, GradePublishService, GradeChangeService
from .serializers import BulkEnterSerializer, GradeRecordSerializer, PublishSerializer, ChangeGradeSerializer


class GradeViewSet(viewsets.ViewSet):
    def list(self, request):
        if request.user.role in ("ADMIN", "REGISTRAR", "MANAGER"):
            qs = GradeRecord.objects.all().order_by("-updated_at")[:200]
        else:
            qs = GradeRecord.objects.filter(student=request.user).order_by("-updated_at")
        return Response(GradeRecordSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"])
    def bulk_enter(self, request):
        ser = BulkEnterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        res = GradeEntryService.bulk_enter(
            instructor=request.user,
            section_id=str(ser.validated_data["section_id"]),
            grades=[{"student_id": x["student_id"], "grade_value": x.get("grade_value")} for x in ser.validated_data["grades"]],
            correlation_id=getattr(request, "request_id", ""),
        )
        return Response(res)

    @action(detail=False, methods=["post"])
    def publish(self, request):
        ser = PublishSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        res = GradePublishService.publish(
            actor=request.user,
            section_id=str(ser.validated_data["section_id"]),
            correlation_id=getattr(request, "request_id", ""),
        )
        return Response(res)

    @action(detail=True, methods=["post"])
    def change(self, request, pk=None):
        ser = ChangeGradeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        res = GradeChangeService.change(
            actor=request.user,
            grade_id=pk,
            new_value=ser.validated_data["new_value"],
            reason=ser.validated_data["reason"],
            correlation_id=getattr(request, "request_id", ""),
        )
        return Response(res)
