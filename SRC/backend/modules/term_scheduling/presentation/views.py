from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from modules.shared.permissions import role_permission
from modules.term_scheduling.infrastructure.models import Term
from modules.term_scheduling.application.services import TermCommandService
from .serializers import TermSerializer, TermStatusSerializer

class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all().order_by("-start_date")
    serializer_class = TermSerializer
    filterset_fields = ["status","code"]
    search_fields = ["code","name"]
    ordering_fields = ["start_date","code"]

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [role_permission("ADMIN","REGISTRAR","MANAGER","INSTRUCTOR","STUDENT")()]
        return [role_permission("ADMIN","REGISTRAR")()]

    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        ser = TermStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        t = TermCommandService.set_status(pk, ser.validated_data["status"], actor=request.user, correlation_id=getattr(request,"request_id",""))
        return Response(self.get_serializer(t).data)
