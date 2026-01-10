from rest_framework import serializers
from modules.certificate.infrastructure.models import CertificateDefinition, CertificateIssue

class CertificateDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateDefinition
        fields = ["id","code","name","description","rules","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]

class CertificateIssueSerializer(serializers.ModelSerializer):
    definition_code = serializers.CharField(source="definition.code", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)
    class Meta:
        model = CertificateIssue
        fields = ["id","definition","definition_code","student","student_username","issued_by","verify_code","status","metadata","created_at"]
        read_only_fields = ["id","verify_code","created_at","issued_by","definition_code","student_username"]

class IssueRequestSerializer(serializers.Serializer):
    definition_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
