from django.test import TestCase
from catalogue.models import Organisation, AIModel, AITool, UseCase, Attestation, Role
from .factories import make_org, make_vendor, make_model, make_tool, make_use_case, make_attestation, make_role


class OrganisationModelTest(TestCase):
    def test_str(self):
        org = make_org(name="HMRC")
        self.assertEqual(str(org), "HMRC")

    def test_org_type_choices(self):
        dept = make_org(org_type="department")
        vendor = make_vendor()
        self.assertEqual(dept.org_type, "department")
        self.assertEqual(vendor.org_type, "vendor")


class AIModelModelTest(TestCase):
    def test_str_with_version(self):
        model = make_model(name="GPT-4", version="turbo")
        self.assertEqual(str(model), "GPT-4 (turbo)")

    def test_str_without_version(self):
        model = make_model(name="Claude", version="")
        self.assertEqual(str(model), "Claude")

    def test_defaults(self):
        model = make_model()
        self.assertFalse(model.training_includes_pii)
        self.assertFalse(model.training_includes_govt_data)
        self.assertEqual(model.explainability_level, "black_box")
        self.assertEqual(model.custom_attributes, {})

    def test_developer_relationship(self):
        vendor = make_vendor(name="Anthropic")
        model = make_model(developer=vendor)
        self.assertEqual(model.developer.name, "Anthropic")


class AIToolModelTest(TestCase):
    def test_str(self):
        tool = make_tool(name="MS Copilot")
        self.assertEqual(str(tool), "MS Copilot")

    def test_default_approval_status(self):
        tool = make_tool(approval_status="pending")
        self.assertEqual(tool.approval_status, "pending")

    def test_ai_models_m2m(self):
        tool = make_tool()
        m1 = make_model(name="Model A", version="1")
        m2 = make_model(name="Model B", version="1", developer=m1.developer)
        tool.ai_models.set([m1, m2])
        self.assertEqual(tool.ai_models.count(), 2)

    def test_reverse_relation_from_model(self):
        tool = make_tool()
        model = make_model()
        tool.ai_models.add(model)
        self.assertIn(tool, model.tools.all())


class UseCaseModelTest(TestCase):
    def test_str(self):
        uc = make_use_case(title="Summarise letters")
        self.assertEqual(str(uc), "Summarise letters")

    def test_defaults(self):
        uc = make_use_case()
        self.assertTrue(uc.human_in_loop)
        self.assertFalse(uc.is_public_facing)
        self.assertEqual(uc.autonomy_level, "human_in_loop")

    def test_tools_m2m(self):
        tool1 = make_tool(name="Tool One")
        tool2 = make_tool(name="Tool Two")
        uc = make_use_case(tool=tool1)
        uc.tools.add(tool2)
        self.assertEqual(uc.tools.count(), 2)

    def test_deleting_tool_does_not_delete_use_case(self):
        tool = make_tool()
        uc = make_use_case(tool=tool)
        pk = uc.pk
        tool.delete()
        self.assertTrue(UseCase.objects.filter(pk=pk).exists())

    def test_reverse_relation_from_tool(self):
        tool = make_tool()
        uc = make_use_case(tool=tool)
        self.assertIn(uc, tool.use_cases.all())


class AttestationModelTest(TestCase):
    def test_str_with_tool(self):
        tool = make_tool(name="Lex")
        att = make_attestation(tool=tool, attestation_type="dpia")
        self.assertIn("DPIA", str(att))
        self.assertIn("Lex", str(att))

    def test_str_with_use_case(self):
        uc = make_use_case(title="Fraud detection")
        att = Attestation.objects.create(use_case=uc, attestation_type="bias", status="pending")
        self.assertIn("Bias Assessment", str(att))
        self.assertIn("Fraud detection", str(att))

    def test_defaults(self):
        att = make_attestation()
        self.assertEqual(att.status, "completed")
        self.assertEqual(att.evidence_url, "")


class RoleModelTest(TestCase):
    def test_str(self):
        tool = make_tool(name="Lex")
        role = make_role(tool=tool, role_type="sro", person_name="Jane Smith")
        self.assertIn("Senior Responsible Owner", str(role))
        self.assertIn("Jane Smith", str(role))
        self.assertIn("Lex", str(role))

    def test_role_on_use_case(self):
        uc = make_use_case()
        role = Role.objects.create(use_case=uc, role_type="dpo", person_name="Bob Jones")
        self.assertEqual(role.use_case, uc)
        self.assertIsNone(role.tool)
