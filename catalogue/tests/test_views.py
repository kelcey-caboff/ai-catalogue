from django.test import TestCase, Client
from django.urls import reverse
from catalogue.models import AITool, AIModel, UseCase
from .factories import make_org, make_vendor, make_model, make_tool, make_use_case, make_attestation, make_role


class HomeViewTest(TestCase):
    def test_home_returns_200(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)

    def test_home_shows_counts(self):
        make_tool()
        make_model()
        make_use_case()
        r = self.client.get(reverse("home"))
        self.assertContains(r, "1")  # counts appear on page

    def test_home_only_shows_approved_tools(self):
        make_tool(name="Approved", approval_status="approved")
        make_tool(name="Pending", approval_status="pending")
        r = self.client.get(reverse("home"))
        self.assertContains(r, "Approved")
        self.assertNotContains(r, "Pending")


class ToolListViewTest(TestCase):
    def test_returns_200(self):
        r = self.client.get(reverse("tool-list"))
        self.assertEqual(r.status_code, 200)

    def test_lists_all_tools(self):
        make_tool(name="Tool A")
        make_tool(name="Tool B")
        r = self.client.get(reverse("tool-list"))
        self.assertContains(r, "Tool A")
        self.assertContains(r, "Tool B")

    def test_search_filters_by_name(self):
        make_tool(name="GitHub Copilot")
        make_tool(name="MS Word")
        r = self.client.get(reverse("tool-list") + "?q=copilot")
        self.assertContains(r, "GitHub Copilot")
        self.assertNotContains(r, "MS Word")

    def test_filter_by_approval_status(self):
        make_tool(name="AlphaTool", approval_status="approved")
        make_tool(name="BetaTool", approval_status="pending")
        r = self.client.get(reverse("tool-list") + "?status=approved")
        self.assertContains(r, "AlphaTool")
        self.assertNotContains(r, "BetaTool")

    def test_filter_by_deployment_type(self):
        make_tool(name="Cloud Tool", deployment_type="cloud")
        make_tool(name="OnPrem Tool", deployment_type="on_premise")
        r = self.client.get(reverse("tool-list") + "?deployment=cloud")
        self.assertContains(r, "Cloud Tool")
        self.assertNotContains(r, "OnPrem Tool")


class ToolDetailViewTest(TestCase):
    def test_returns_200(self):
        tool = make_tool()
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertEqual(r.status_code, 200)

    def test_returns_404_for_missing(self):
        r = self.client.get(reverse("tool-detail", args=[99999]))
        self.assertEqual(r.status_code, 404)

    def test_shows_tool_name_and_vendor(self):
        vendor = make_vendor(name="Acme Ltd")
        tool = make_tool(name="SuperAI", vendor=vendor)
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "SuperAI")
        self.assertContains(r, "Acme Ltd")

    def test_shows_ai_models(self):
        tool = make_tool()
        model = make_model(name="Claude")
        tool.ai_models.add(model)
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "Claude")

    def test_shows_use_cases(self):
        tool = make_tool()
        make_use_case(title="Summarise letters", tool=tool)
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "Summarise letters")

    def test_shows_roles(self):
        tool = make_tool()
        make_role(tool=tool, person_name="Jane Smith")
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "Jane Smith")

    def test_shows_attestations(self):
        tool = make_tool()
        make_attestation(tool=tool, attestation_type="dpia", status="completed")
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "DPIA")

    def test_shows_external_links(self):
        tool = make_tool(ardoq_link="https://ardoq.example.com/123")
        r = self.client.get(reverse("tool-detail", args=[tool.pk]))
        self.assertContains(r, "Ardoq architecture record")


class ModelListViewTest(TestCase):
    def test_returns_200(self):
        r = self.client.get(reverse("model-list"))
        self.assertEqual(r.status_code, 200)

    def test_lists_models(self):
        make_model(name="GPT-4", version="turbo")
        r = self.client.get(reverse("model-list"))
        self.assertContains(r, "GPT-4")

    def test_search_by_name(self):
        make_model(name="GPT-4", version="1")
        make_model(name="BERT", version="1")
        r = self.client.get(reverse("model-list") + "?q=gpt")
        self.assertContains(r, "GPT-4")
        self.assertNotContains(r, "BERT")

    def test_filter_by_type(self):
        make_model(name="LLM A", version="1", model_type="llm")
        make_model(name="Classifier B", version="1", model_type="classifier")
        r = self.client.get(reverse("model-list") + "?type=classifier")
        self.assertContains(r, "Classifier B")
        self.assertNotContains(r, "LLM A")


class ModelDetailViewTest(TestCase):
    def test_returns_200(self):
        model = make_model()
        r = self.client.get(reverse("model-detail", args=[model.pk]))
        self.assertEqual(r.status_code, 200)

    def test_returns_404_for_missing(self):
        r = self.client.get(reverse("model-detail", args=[99999]))
        self.assertEqual(r.status_code, 404)

    def test_shows_model_details(self):
        vendor = make_vendor(name="Anthropic")
        model = make_model(
            name="Claude",
            version="3",
            developer=vendor,
            context_window_size=200000,
            training_includes_pii=True,
        )
        r = self.client.get(reverse("model-detail", args=[model.pk]))
        self.assertContains(r, "Claude")
        self.assertContains(r, "Anthropic")
        self.assertContains(r, "200")  # context window
        self.assertContains(r, "Yes")  # PII flag

    def test_shows_tools_using_model(self):
        tool = make_tool(name="SuperPlatform")
        model = make_model()
        tool.ai_models.add(model)
        r = self.client.get(reverse("model-detail", args=[model.pk]))
        self.assertContains(r, "SuperPlatform")


class UseCaseListViewTest(TestCase):
    def test_returns_200(self):
        r = self.client.get(reverse("usecase-list"))
        self.assertEqual(r.status_code, 200)

    def test_lists_use_cases(self):
        make_use_case(title="Summarise letters")
        r = self.client.get(reverse("usecase-list"))
        self.assertContains(r, "Summarise letters")

    def test_filter_by_risk(self):
        make_use_case(title="Low risk job", risk_level="low")
        make_use_case(title="Critical job", risk_level="critical")
        r = self.client.get(reverse("usecase-list") + "?risk=critical")
        self.assertContains(r, "Critical job")
        self.assertNotContains(r, "Low risk job")

    def test_search(self):
        make_use_case(title="Fraud detection")
        make_use_case(title="Document summarisation")
        r = self.client.get(reverse("usecase-list") + "?q=fraud")
        self.assertContains(r, "Fraud detection")
        self.assertNotContains(r, "Document summarisation")


class UseCaseDetailViewTest(TestCase):
    def test_returns_200(self):
        uc = make_use_case()
        r = self.client.get(reverse("usecase-detail", args=[uc.pk]))
        self.assertEqual(r.status_code, 200)

    def test_returns_404_for_missing(self):
        r = self.client.get(reverse("usecase-detail", args=[99999]))
        self.assertEqual(r.status_code, 404)

    def test_shows_use_case_details(self):
        dept = make_org(name="DWP", org_type="department")
        tool = make_tool(name="ClaimBot")
        uc = make_use_case(
            title="Assess claims",
            tool=tool,
            owning_department=dept,
            risk_level="high",
            is_public_facing=True,
        )
        r = self.client.get(reverse("usecase-detail", args=[uc.pk]))
        self.assertContains(r, "Assess claims")
        self.assertContains(r, "DWP")
        self.assertContains(r, "ClaimBot")
        self.assertContains(r, "Yes")  # public facing
