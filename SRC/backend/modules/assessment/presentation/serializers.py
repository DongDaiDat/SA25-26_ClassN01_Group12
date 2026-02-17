from rest_framework import serializers
from modules.assessment.infrastructure.models import GradeRecord, SectionGradePolicy, GradeChangeLog


class GradeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeRecord
        fields = [
            "id",
            "student",
            "section_id",
            "term_id",
            "course_id",
            "grade_value",
            "grade_scale",
            "status",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class BulkGradeItemSerializer(serializers.Serializer):
    # NOTE: In this codebase, User.id is INTEGER (not UUID)
    student_id = serializers.IntegerField()
    grade_value = serializers.FloatField(required=False, allow_null=True)


class BulkEnterSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()
    grades = serializers.ListField(child=BulkGradeItemSerializer())


class PublishSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()


class ChangeGradeSerializer(serializers.Serializer):
    new_value = serializers.FloatField()
    reason = serializers.CharField(max_length=255)
