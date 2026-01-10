from rest_framework import serializers
from modules.program.infrastructure.models import Program, CurriculumVersion, CurriculumNode, CurriculumRule

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id","code","name","status","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class CurriculumVersionSerializer(serializers.ModelSerializer):
    program_code = serializers.CharField(source="program.code", read_only=True)
    class Meta:
        model = CurriculumVersion
        fields = ["id","program","program_code","version_code","status","effective_year","notes","created_at","updated_at"]
        read_only_fields = ["id","status","created_at","updated_at"]

class CurriculumNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumNode
        fields = ["id","curriculum","parent","node_type","title","sort_order","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class CurriculumRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumRule
        fields = ["id","node","rule_type","params","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]
