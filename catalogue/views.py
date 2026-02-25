from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count, Prefetch
from .models import AITool, AIModel, UseCase, Organisation, Attestation


class HomeView(ListView):
    model = AITool
    template_name = "public/home.html"
    context_object_name = "tools"
    queryset = AITool.objects.select_related("vendor").filter(
        approval_status="approved"
    ).order_by("name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_tools"] = AITool.objects.count()
        ctx["total_models"] = AIModel.objects.count()
        ctx["total_use_cases"] = UseCase.objects.count()
        return ctx


class ToolListView(ListView):
    model = AITool
    template_name = "public/tool_list.html"
    context_object_name = "tools"
    paginate_by = 20

    def get_queryset(self):
        qs = AITool.objects.select_related("vendor").prefetch_related("ai_models").order_by("name")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        deployment = self.request.GET.get("deployment")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(vendor__name__icontains=q))
        if status:
            qs = qs.filter(approval_status=status)
        if deployment:
            qs = qs.filter(deployment_type=deployment)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["approval_choices"] = AITool.ApprovalStatus.choices
        ctx["deployment_choices"] = AITool.DeploymentType.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_status"] = self.request.GET.get("status", "")
        ctx["selected_deployment"] = self.request.GET.get("deployment", "")
        return ctx


class ToolDetailView(DetailView):
    model = AITool
    template_name = "public/tool_detail.html"
    context_object_name = "tool"
    queryset = AITool.objects.select_related("vendor").prefetch_related(
        "ai_models__developer", "use_cases__owning_department", "attestations", "roles"
    )


class ModelListView(ListView):
    model = AIModel
    template_name = "public/model_list.html"
    context_object_name = "models"
    paginate_by = 20

    def get_queryset(self):
        qs = AIModel.objects.select_related("developer").order_by("name")
        q = self.request.GET.get("q")
        model_type = self.request.GET.get("type")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(developer__name__icontains=q))
        if model_type:
            qs = qs.filter(model_type=model_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["type_choices"] = AIModel.ModelType.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_type"] = self.request.GET.get("type", "")
        return ctx


class ModelDetailView(DetailView):
    model = AIModel
    template_name = "public/model_detail.html"
    context_object_name = "ai_model"
    queryset = AIModel.objects.select_related("developer").prefetch_related("tools__vendor")


class UseCaseListView(ListView):
    model = UseCase
    template_name = "public/usecase_list.html"
    context_object_name = "use_cases"
    paginate_by = 20

    def get_queryset(self):
        qs = UseCase.objects.select_related("owning_department").prefetch_related("tools").order_by("title")
        q = self.request.GET.get("q")
        risk = self.request.GET.get("risk")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if risk:
            qs = qs.filter(risk_level=risk)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["risk_choices"] = UseCase.RiskLevel.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_risk"] = self.request.GET.get("risk", "")
        return ctx


class UseCaseDetailView(DetailView):
    model = UseCase
    template_name = "public/usecase_detail.html"
    context_object_name = "use_case"
    queryset = UseCase.objects.select_related("owning_department").prefetch_related(
        "tools__vendor", "attestations", "roles"
    )


class AssuredToolsView(ListView):
    """Approved tools with their assurance posture at a glance."""
    template_name = "public/assured.html"
    context_object_name = "tools"

    def get_queryset(self):
        return (
            AITool.objects
            .filter(approval_status="approved")
            .select_related("vendor")
            .prefetch_related(
                Prefetch(
                    "attestations",
                    queryset=Attestation.objects.order_by("attestation_type"),
                ),
                "roles",
                "use_cases__owning_department",
            )
            .order_by("name")
        )


class HorizonView(ListView):
    """Tools we know about but that are not yet approved — CRM / pipeline view."""
    template_name = "public/horizon.html"
    context_object_name = "tools"

    def get_queryset(self):
        return (
            AITool.objects
            .filter(approval_status__in=["pending", "under_review", "rejected", "suspended"])
            .select_related("vendor")
            .prefetch_related("roles", "use_cases")
            .order_by("approval_status", "name")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["pending"] = qs.filter(approval_status="pending")
        ctx["under_review"] = qs.filter(approval_status="under_review")
        ctx["rejected"] = qs.filter(approval_status="rejected")
        ctx["suspended"] = qs.filter(approval_status="suspended")
        return ctx


class ByDepartmentView(TemplateView):
    """Use cases grouped by owning department."""
    template_name = "public/by_department.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        departments = (
            Organisation.objects
            .filter(org_type="department")
            .prefetch_related(
                Prefetch(
                    "use_cases",
                    queryset=UseCase.objects.prefetch_related("tools").order_by("title"),
                )
            )
            .annotate(use_case_count=Count("use_cases"))
            .filter(use_case_count__gt=0)
            .order_by("name")
        )
        ctx["departments"] = departments
        ctx["unowned"] = UseCase.objects.filter(owning_department__isnull=True).prefetch_related("tools").order_by("title")
        return ctx


class ModelMapView(ListView):
    """Which AI models underpin which tools — useful for understanding dependencies."""
    template_name = "public/model_map.html"
    context_object_name = "ai_models"

    def get_queryset(self):
        return (
            AIModel.objects
            .select_related("developer")
            .prefetch_related(
                Prefetch(
                    "tools",
                    queryset=AITool.objects.select_related("vendor").order_by("name"),
                )
            )
            .annotate(tool_count=Count("tools"))
            .order_by("-tool_count", "name")
        )
