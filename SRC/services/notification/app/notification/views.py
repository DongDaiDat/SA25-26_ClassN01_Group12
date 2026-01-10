from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NotificationMessage
from .serializers import NotificationMessageSerializer, ManualSendSerializer
from .provider import send_mock

class NotificationMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationMessage.objects.all().order_by("-created_at")
    serializer_class = NotificationMessageSerializer
    filterset_fields = ["status","event_type","channel"]
    search_fields = ["to","subject","event_id","correlation_id"]
    ordering_fields = ["created_at","status"]

class ManualSendViewSet(viewsets.ViewSet):
    def create(self, request):
        ser = ManualSendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        resp = send_mock(data["channel"], data["to"], data.get("subject",""), data.get("body",""))
        msg = NotificationMessage.objects.create(
            channel=data["channel"],
            to=data["to"],
            subject=data.get("subject",""),
            body=data.get("body",""),
            status=NotificationMessage.STATUS_SENT,
            provider_response=resp,
        )
        return Response(NotificationMessageSerializer(msg).data, status=201)
