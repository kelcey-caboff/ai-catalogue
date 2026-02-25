from rest_framework import serializers
from catalogue.models import Organisation, AIModel, AITool, UseCase, Attestation, Role


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = "__all__"


class AIModelSerializer(serializers.ModelSerializer):
    developer_name = serializers.CharField(source="developer.name", read_only=True)

    class Meta:
        model = AIModel
        fields = "__all__"


class AttestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attestation
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UseCaseSerializer(serializers.ModelSerializer):
    attestations = AttestationSerializer(many=True, read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    tool_names = serializers.SlugRelatedField(source="tools", many=True, read_only=True, slug_field="name")
    owning_department_name = serializers.CharField(source="owning_department.name", read_only=True)

    class Meta:
        model = UseCase
        fields = "__all__"


class AIToolSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    models_detail = AIModelSerializer(source="ai_models", many=True, read_only=True)
    use_cases = UseCaseSerializer(many=True, read_only=True)
    attestations = AttestationSerializer(many=True, read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = AITool
        fields = "__all__"


class AIToolListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)

    class Meta:
        model = AITool
        fields = [
            "id", "name", "description", "vendor_name", "product_type",
            "deployment_type", "approval_status", "last_assessment_date",
        ]
