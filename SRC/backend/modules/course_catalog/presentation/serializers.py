from rest_framework import serializers
from modules.course_catalog.infrastructure.models import Course, CoursePrerequisite

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id","code","name","credits","status","description","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class CoursePrerequisiteSerializer(serializers.ModelSerializer):
    prereq_course_code = serializers.CharField(source="prereq_course.code", read_only=True)
    class Meta:
        model = CoursePrerequisite
        fields = ["id","course","prereq_course","prereq_course_code","min_grade","created_at"]
        read_only_fields = ["id","created_at","prereq_course_code"]

class SetPrereqSerializer(serializers.Serializer):
    prereq_course_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)
