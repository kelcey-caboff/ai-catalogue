from django.db import models


class Organisation(models.Model):
    class OrgType(models.TextChoices):
        DEPARTMENT = "department", "Government Department"
        VENDOR = "vendor", "Vendor"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AIModel(models.Model):
    class ModelType(models.TextChoices):
        LLM = "llm", "Large Language Model"
        MULTIMODAL = "multimodal", "Multimodal"
        EMBEDDING = "embedding", "Embedding"
        CLASSIFIER = "classifier", "Classifier"
        PREDICTOR = "predictor", "Predictor"
        ANOMALY = "anomaly", "Anomaly Detector"
        RECOMMENDER = "recommender", "Recommender"
        NER = "ner", "NER Model"
        OTHER = "other", "Other"

    class ExplainabilityLevel(models.TextChoices):
        BLACK_BOX = "black_box", "Black Box"
        PARTIAL = "partial", "Partial Explainability"
        FULL = "full", "Full Explainability"

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=100, blank=True)
    developer = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="developed_models",
    )
    model_type = models.CharField(max_length=20, choices=ModelType.choices, default=ModelType.OTHER)
    parameter_count = models.BigIntegerField(null=True, blank=True, help_text="Number of parameters")
    context_window_size = models.IntegerField(null=True, blank=True, help_text="Context window size in tokens")
    training_cutoff_date = models.DateField(null=True, blank=True)
    training_includes_pii = models.BooleanField(default=False)
    training_includes_govt_data = models.BooleanField(default=False)
    explainability_level = models.CharField(
        max_length=20,
        choices=ExplainabilityLevel.choices,
        default=ExplainabilityLevel.BLACK_BOX,
    )
    ardoq_link = models.URLField(blank=True, help_text="Link to record in Ardoq")
    informatica_link = models.URLField(blank=True, help_text="Link to dataset in Informatica")
    contract_link = models.URLField(blank=True, help_text="Link to contract in Atamis")
    notes = models.TextField(blank=True)
    custom_attributes = models.JSONField(default=dict, blank=True, help_text="Additional key/value attributes")

    class Meta:
        ordering = ["name", "version"]
        verbose_name = "AI Model"

    def __str__(self):
        if self.version:
            return f"{self.name} ({self.version})"
        return self.name


class AITool(models.Model):
    class DeploymentType(models.TextChoices):
        CLOUD = "cloud", "Cloud"
        ON_PREMISE = "on_premise", "On-Premise"
        HYBRID = "hybrid", "Hybrid"

    class LicensingModel(models.TextChoices):
        COMMERCIAL = "commercial", "Commercial"
        OPEN_SOURCE = "open_source", "Open Source"
        IN_HOUSE = "in_house", "In-House"

    class ProductType(models.TextChoices):
        PRODUCT = "product", "Product"
        SERVICE = "service", "Service"
        PLATFORM = "platform", "Platform"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"
        UNDER_REVIEW = "under_review", "Under Review"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, help_text="Public URL for the tool or product")
    vendor = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tools",
    )
    deployment_type = models.CharField(max_length=20, choices=DeploymentType.choices, blank=True)
    licensing_model = models.CharField(max_length=20, choices=LicensingModel.choices, blank=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices, blank=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    ai_models = models.ManyToManyField(AIModel, blank=True, related_name="tools")
    ardoq_link = models.URLField(blank=True, help_text="Link to record in Ardoq")
    informatica_link = models.URLField(blank=True, help_text="Link to dataset in Informatica")
    contract_link = models.URLField(blank=True, help_text="Link to contract in Atamis")
    data_residency = models.CharField(max_length=255, blank=True)
    security_certification = models.CharField(max_length=255, blank=True)
    last_assessment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    custom_attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "AI Tool / Platform"
        verbose_name_plural = "AI Tools / Platforms"

    def __str__(self):
        return self.name


class UseCase(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class AutonomyLevel(models.TextChoices):
        HUMAN_DRIVEN = "human_driven", "Human-Driven"
        HUMAN_IN_LOOP = "human_in_loop", "Human-in-Loop"
        HUMAN_ON_LOOP = "human_on_loop", "Human-on-Loop"
        AUTONOMOUS = "autonomous", "Autonomous"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tools = models.ManyToManyField(AITool, blank=True, related_name="use_cases")
    owning_department = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="use_cases",
    )
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    autonomy_level = models.CharField(
        max_length=20,
        choices=AutonomyLevel.choices,
        default=AutonomyLevel.HUMAN_IN_LOOP,
    )
    human_in_loop = models.BooleanField(default=True)
    is_public_facing = models.BooleanField(default=False)
    impacted_population = models.TextField(blank=True)
    custom_attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Attestation(models.Model):
    class AttestationType(models.TextChoices):
        DPIA = "dpia", "DPIA"
        BIAS = "bias", "Bias Assessment"
        SECURITY = "security", "Security Review"
        ETHICS = "ethics", "Ethics Review"
        LEGAL = "legal", "Legal Review"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"

    attestation_type = models.CharField(max_length=20, choices=AttestationType.choices)
    tool = models.ForeignKey(
        AITool,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attestations",
    )
    use_case = models.ForeignKey(
        UseCase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attestations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    evidence_url = models.URLField(blank=True)
    attestation_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-attestation_date"]

    def __str__(self):
        subject = self.tool or self.use_case or "Unknown"
        return f"{self.get_attestation_type_display()} — {subject}"


class Role(models.Model):
    class RoleType(models.TextChoices):
        SRO = "sro", "Senior Responsible Owner"
        DPO = "dpo", "Data Protection Officer"
        SECURITY = "security", "Security Officer"
        ETHICS = "ethics", "Ethics Officer"
        ARCHITECT = "architect", "Technical Architect"
        LEGAL = "legal", "Legal Counsel"
        OTHER = "other", "Other"

    person_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    role_type = models.CharField(max_length=20, choices=RoleType.choices)
    tool = models.ForeignKey(
        AITool,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
    )
    use_case = models.ForeignKey(
        UseCase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
    )

    class Meta:
        ordering = ["role_type", "person_name"]

    def __str__(self):
        subject = self.tool or self.use_case or "Unassigned"
        return f"{self.get_role_type_display()}: {self.person_name} ({subject})"
