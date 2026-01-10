from rest_framework import serializers
from modules.term_scheduling.infrastructure.models import Term

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["id","code","name","start_date","end_date","enroll_open_at","enroll_close_at","status","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class TermStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[("DRAFT","DRAFT"),("OPEN","OPEN"),("LOCKED","LOCKED"),("CLOSED","CLOSED")])
