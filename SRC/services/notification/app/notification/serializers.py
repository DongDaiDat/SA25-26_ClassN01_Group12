from rest_framework import serializers
from .models import NotificationMessage

class NotificationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationMessage
        fields = ["id","created_at","event_id","event_type","channel","to","subject","body","status","provider_response","retry_count","correlation_id"]
        read_only_fields = ["id","created_at","status","provider_response","retry_count"]

class ManualSendSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=[("EMAIL","EMAIL"),("SMS","SMS")], default="EMAIL")
    to = serializers.CharField(max_length=255)
    subject = serializers.CharField(max_length=255, required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
