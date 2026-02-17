from rest_framework import serializers
from modules.enrollment.infrastructure.models import Enrollment


class EnrollSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()


class OverrideEnrollSerializer(serializers.Serializer):
    # FIX: User PK là Integer => dùng IntegerField
    student_id = serializers.IntegerField(min_value=1)
    section_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=255)


class EnrollmentSerializer(serializers.ModelSerializer):
    # (Optional) thêm username để UI hiển thị roster dễ hơn
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_username", "section_id", "term_id", "course_id", "status", "source", "reason", "created_at", "canceled_at"]
        read_only_fields = fields
