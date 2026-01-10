from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from modules.shared.permissions import role_permission
from modules.class_section.infrastructure.models import Room, Section, ScheduleSlot, SectionInstructor
from modules.class_section.application.services import SectionCommandService
from .serializers import RoomSerializer, SectionSerializer, ScheduleSlotSerializer, SectionInstructorSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by("code")
    serializer_class = RoomSerializer
    search_fields = ["code","name"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER","INSTRUCTOR","STUDENT")()]
        return [role_permission("ADMIN","REGISTRAR")()]

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all().order_by("-created_at")
    serializer_class = SectionSerializer
    filterset_fields = ["term_id","course_id","status"]
    search_fields = ["section_code"]
    ordering_fields = ["created_at","section_code","capacity"]

    def get_permissions(self):
        if self.action in ("list","retrieve","search"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER","INSTRUCTOR","STUDENT")()]
        return [role_permission("ADMIN","REGISTRAR")()]

    def perform_create(self, serializer):
        term_id = str(self.request.data.get("term_id"))
        course_id = str(self.request.data.get("course_id"))
        SectionCommandService.validate_refs(term_id=term_id, course_id=course_id)
        serializer.save()

    def perform_update(self, serializer):
        term_id = str(self.request.data.get("term_id", serializer.instance.term_id))
        course_id = str(self.request.data.get("course_id", serializer.instance.course_id))
        SectionCommandService.validate_refs(term_id=term_id, course_id=course_id)
        serializer.save()

    @action(detail=True, methods=["get","put"])
    def schedule(self, request, pk=None):
        if request.method.lower() == "get":
            qs = ScheduleSlot.objects.filter(section_id=pk).order_by("day_of_week","start_time")
            return Response(ScheduleSlotSerializer(qs, many=True).data)
        if request.user.role not in ("ADMIN","REGISTRAR"):
            return Response({"error":{"code":"FORBIDDEN","message":"not allowed","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        slots = request.data if isinstance(request.data, list) else []
        ScheduleSlot.objects.filter(section_id=pk).delete()
        created = []
        for s in slots:
            ser = ScheduleSlotSerializer(data={**s, "section": pk})
            ser.is_valid(raise_exception=True)
            created.append(ser.save())
        return Response(ScheduleSlotSerializer(created, many=True).data)

    @action(detail=True, methods=["get","post"])
    def instructors(self, request, pk=None):
        if request.method.lower() == "get":
            qs = SectionInstructor.objects.select_related("instructor").filter(section_id=pk)
            return Response(SectionInstructorSerializer(qs, many=True).data)
        if request.user.role not in ("ADMIN","REGISTRAR"):
            return Response({"error":{"code":"FORBIDDEN","message":"not allowed","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        ser = SectionInstructorSerializer(data={**request.data, "section": pk})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(SectionInstructorSerializer(obj).data, status=201)

class ScheduleSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScheduleSlot.objects.select_related("section","room").all()
    serializer_class = ScheduleSlotSerializer
    filterset_fields = ["section","day_of_week"]
