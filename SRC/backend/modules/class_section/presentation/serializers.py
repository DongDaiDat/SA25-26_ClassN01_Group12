from rest_framework import serializers
from modules.class_section.infrastructure.models import Room, Section, ScheduleSlot, SectionInstructor
from modules.class_section.application.services import SectionQueryService

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id","code","name","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class SectionSerializer(serializers.ModelSerializer):
    term_code = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ["id","term_id","term_code","course_id","course_code","section_code","capacity","enrolled_count","status","created_at","updated_at"]
        read_only_fields = ["id","enrolled_count","created_at","updated_at","term_code","course_code"]

    def get_term_code(self, obj):
        try:
            return SectionQueryService.get_term_code(str(obj.term_id))
        except Exception:
            return ""

    def get_course_code(self, obj):
        try:
            return SectionQueryService.get_course_code(str(obj.course_id))
        except Exception:
            return ""

class SectionInstructorSerializer(serializers.ModelSerializer):
    instructor_username = serializers.CharField(source="instructor.username", read_only=True)
    class Meta:
        model = SectionInstructor
        fields = ["id","section","instructor","instructor_username","created_at"]
        read_only_fields = ["id","created_at","instructor_username"]

class ScheduleSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleSlot
        fields = ["id","section","day_of_week","start_time","end_time","room","created_at"]
        read_only_fields = ["id","created_at"]
