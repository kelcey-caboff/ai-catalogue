from django.contrib import admin
from .models import Organisation, AIModel, AITool, UseCase, Attestation, Role

admin.site.site_header = "AI Catalogue"
admin.site.site_title = "AI Catalogue Admin"
admin.site.index_title = "Manage the catalogue"


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ["name", "org_type", "website"]
    list_filter = ["org_type"]
    search_fields = ["name"]


class RoleInline(admin.TabularInline):
    model = Role
    extra = 1
    fields = ["role_type", "person_name", "email"]


class AttestationInline(admin.TabularInline):
    model = Attestation
    extra = 1
    fields = ["attestation_type", "status", "attestation_date", "expiry_date", "evidence_url"]


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ["name", "version", "developer", "model_type", "explainability_level", "training_cutoff_date"]
    list_filter = ["model_type", "explainability_level", "training_includes_pii", "training_includes_govt_data"]
    search_fields = ["name", "developer__name"]
    autocomplete_fields = ["developer"]
    fieldsets = [
        (None, {
            "fields": ["name", "version", "developer", "model_type", "explainability_level"],
        }),
        ("Technical details", {
            "fields": ["parameter_count", "context_window_size", "training_cutoff_date"],
            "classes": ["collapse"],
        }),
        ("Training data", {
            "fields": ["training_includes_pii", "training_includes_govt_data"],
            "classes": ["collapse"],
        }),
        ("External links", {
            "fields": ["ardoq_link", "informatica_link", "contract_link"],
            "classes": ["collapse"],
        }),
        ("Additional", {
            "fields": ["notes", "custom_attributes"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ["name", "vendor", "product_type", "deployment_type", "approval_status", "last_assessment_date"]
    list_filter = ["approval_status", "deployment_type", "licensing_model", "product_type"]
    search_fields = ["name", "vendor__name"]
    autocomplete_fields = ["vendor"]
    filter_horizontal = ["ai_models"]
    inlines = [RoleInline, AttestationInline]
    fieldsets = [
        (None, {
            "fields": ["name", "description", "website", "vendor", "product_type", "licensing_model", "deployment_type", "approval_status"],
        }),
        ("Models", {
            "fields": ["ai_models"],
        }),
        ("External links", {
            "fields": ["ardoq_link", "informatica_link", "contract_link"],
            "classes": ["collapse"],
        }),
        ("Compliance", {
            "fields": ["data_residency", "security_certification", "last_assessment_date"],
            "classes": ["collapse"],
        }),
        ("Additional", {
            "fields": ["notes", "custom_attributes"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ["title", "owning_department", "risk_level", "autonomy_level", "is_public_facing"]
    list_filter = ["risk_level", "autonomy_level", "is_public_facing", "human_in_loop"]
    search_fields = ["title", "tools__name", "owning_department__name"]
    autocomplete_fields = ["owning_department"]
    filter_horizontal = ["tools"]
    inlines = [RoleInline, AttestationInline]


@admin.register(Attestation)
class AttestationAdmin(admin.ModelAdmin):
    list_display = ["attestation_type", "tool", "use_case", "status", "attestation_date", "expiry_date"]
    list_filter = ["attestation_type", "status"]
    search_fields = ["tool__name", "use_case__title"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["person_name", "role_type", "email", "tool", "use_case"]
    list_filter = ["role_type"]
    search_fields = ["person_name", "email", "tool__name", "use_case__title"]
