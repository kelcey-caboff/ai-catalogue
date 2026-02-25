from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from catalogue.models import Organisation, AIModel, AITool, UseCase, Attestation, Role
from .serializers import (
    OrganisationSerializer,
    AIModelSerializer,
    AIToolSerializer,
    AIToolListSerializer,
    UseCaseSerializer,
    AttestationSerializer,
    RoleSerializer,
)


class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    filterset_fields = ["org_type"]
    search_fields = ["name"]
    ordering_fields = ["name", "org_type"]


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.select_related("developer").all()
    serializer_class = AIModelSerializer
    filterset_fields = ["model_type", "explainability_level", "training_includes_pii", "training_includes_govt_data"]
    search_fields = ["name", "developer__name"]
    ordering_fields = ["name", "training_cutoff_date"]


class AIToolViewSet(viewsets.ModelViewSet):
    queryset = AITool.objects.select_related("vendor").prefetch_related(
        "ai_models", "use_cases", "attestations", "roles"
    ).all()
    filterset_fields = ["approval_status", "deployment_type", "licensing_model", "product_type"]
    search_fields = ["name", "vendor__name", "description"]
    ordering_fields = ["name", "approval_status", "last_assessment_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return AIToolListSerializer
        return AIToolSerializer


class UseCaseViewSet(viewsets.ModelViewSet):
    queryset = UseCase.objects.select_related("owning_department").prefetch_related(
        "tools", "attestations", "roles"
    ).all()
    serializer_class = UseCaseSerializer
    filterset_fields = ["risk_level", "autonomy_level", "is_public_facing", "human_in_loop", "tools"]
    search_fields = ["title", "description", "tools__name"]
    ordering_fields = ["title", "risk_level"]


class AttestationViewSet(viewsets.ModelViewSet):
    queryset = Attestation.objects.select_related("tool", "use_case").all()
    serializer_class = AttestationSerializer
    filterset_fields = ["attestation_type", "status", "tool", "use_case"]
    search_fields = ["tool__name", "use_case__title"]
    ordering_fields = ["attestation_date", "expiry_date"]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.select_related("tool", "use_case").all()
    serializer_class = RoleSerializer
    filterset_fields = ["role_type", "tool", "use_case"]
    search_fields = ["person_name", "email", "tool__name"]
    ordering_fields = ["role_type", "person_name"]
