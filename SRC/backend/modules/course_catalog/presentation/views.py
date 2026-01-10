from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from modules.shared.permissions import role_permission
from modules.course_catalog.infrastructure.models import Course, CoursePrerequisite
from modules.course_catalog.application.services import CoursePrereqService, CourseQueryService
from .serializers import CourseSerializer, CoursePrerequisiteSerializer, SetPrereqSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("code")
    serializer_class = CourseSerializer
    filterset_fields = ["status","credits"]
    search_fields = ["code","name"]
    ordering_fields = ["code","credits","created_at"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER","INSTRUCTOR","STUDENT")()]
        return [role_permission("ADMIN","REGISTRAR")()]

    @action(detail=True, methods=["get","put"])
    def prerequisites(self, request, pk=None):
        if request.method.lower() == "get":
            qs = CoursePrerequisite.objects.select_related("prereq_course").filter(course_id=pk)
            return Response(CoursePrerequisiteSerializer(qs, many=True).data)
        # put
        if request.user.role not in ("ADMIN","REGISTRAR"):
            return Response({"error": {"code":"FORBIDDEN","message":"not allowed","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=403)
        ser = SetPrereqSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        rules = CoursePrereqService.set_prerequisites(str(pk), [str(x) for x in ser.validated_data["prereq_course_ids"]],
                                                      actor=request.user, correlation_id=getattr(request,"request_id",""))
        return Response([r.__dict__ for r in rules])
