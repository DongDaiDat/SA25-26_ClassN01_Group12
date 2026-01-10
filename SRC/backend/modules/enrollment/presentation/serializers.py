from rest_framework import serializers
from modules.enrollment.infrastructure.models import Enrollment

class EnrollSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()

class OverrideEnrollSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    section_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=255)

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id","student","section_id","term_id","course_id","status","source","reason","created_at","canceled_at"]
        read_only_fields = fields
