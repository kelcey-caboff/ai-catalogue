"""
Simple factory helpers to create test fixtures without a third-party library.
"""
from catalogue.models import Organisation, AIModel, AITool, UseCase, Attestation, Role


def make_org(name="HMRC", org_type="department", **kwargs):
    return Organisation.objects.create(name=name, org_type=org_type, **kwargs)


def make_vendor(name="Acme AI Ltd", **kwargs):
    return Organisation.objects.create(name=name, org_type="vendor", **kwargs)


def make_model(name="GPT-4", version="1.0", developer=None, model_type="llm", **kwargs):
    if developer is None:
        developer = make_vendor(name="OpenAI")
    return AIModel.objects.create(
        name=name,
        version=version,
        developer=developer,
        model_type=model_type,
        **kwargs,
    )


def make_tool(name="CoPilot", vendor=None, approval_status="approved", **kwargs):
    if vendor is None:
        vendor = make_vendor()
    return AITool.objects.create(
        name=name,
        vendor=vendor,
        approval_status=approval_status,
        **kwargs,
    )


def make_use_case(title="Summarise letters", tool=None, risk_level="low", **kwargs):
    uc = UseCase.objects.create(title=title, risk_level=risk_level, **kwargs)
    if tool is None:
        tool = make_tool()
    uc.tools.add(tool)
    return uc


def make_attestation(tool=None, attestation_type="dpia", status="completed", **kwargs):
    if tool is None:
        tool = make_tool()
    return Attestation.objects.create(
        tool=tool,
        attestation_type=attestation_type,
        status=status,
        **kwargs,
    )


def make_role(tool=None, role_type="sro", person_name="Jane Smith", **kwargs):
    if tool is None:
        tool = make_tool()
    return Role.objects.create(
        tool=tool,
        role_type=role_type,
        person_name=person_name,
        **kwargs,
    )
