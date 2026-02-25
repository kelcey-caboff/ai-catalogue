from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from catalogue.models import AITool, AIModel, UseCase, Organisation, Attestation, Role
from .factories import make_org, make_vendor, make_model, make_tool, make_use_case, make_attestation, make_role


class APIAuthMixin:
    """Provide an authenticated client and an unauthenticated client."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def anon_client(self):
        from rest_framework.test import APIClient
        return APIClient()


class OrganisationAPITest(APIAuthMixin, APITestCase):
    def test_list_empty(self):
        r = self.client.get("/api/v1/organisations/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 0)

    def test_create(self):
        r = self.client.post("/api/v1/organisations/", {"name": "HMRC", "org_type": "department"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organisation.objects.count(), 1)

    def test_retrieve(self):
        org = make_org()
        r = self.client.get(f"/api/v1/organisations/{org.pk}/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["name"], org.name)

    def test_filter_by_type(self):
        make_org(name="HMRC", org_type="department")
        make_vendor(name="Acme")
        r = self.client.get("/api/v1/organisations/?org_type=vendor")
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["name"], "Acme")

    def test_search(self):
        make_org(name="HMRC")
        make_org(name="DVLA")
        r = self.client.get("/api/v1/organisations/?search=HMRC")
        self.assertEqual(r.data["count"], 1)

    def test_unauthenticated_read_allowed(self):
        make_org()
        r = self.anon_client().get("/api/v1/organisations/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_unauthenticated_write_denied(self):
        r = self.anon_client().post("/api/v1/organisations/", {"name": "X", "org_type": "vendor"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class AIModelAPITest(APIAuthMixin, APITestCase):
    def test_list(self):
        make_model()
        r = self.client.get("/api/v1/models/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 1)

    def test_create(self):
        vendor = make_vendor()
        r = self.client.post("/api/v1/models/", {
            "name": "Claude",
            "version": "3",
            "developer": vendor.pk,
            "model_type": "llm",
            "explainability_level": "black_box",
            "training_includes_pii": False,
            "training_includes_govt_data": False,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_filter_by_model_type(self):
        make_model(model_type="llm")
        make_model(name="BERT", version="1", model_type="classifier")
        r = self.client.get("/api/v1/models/?model_type=llm")
        self.assertEqual(r.data["count"], 1)

    def test_developer_name_in_response(self):
        vendor = make_vendor(name="Anthropic")
        make_model(developer=vendor)
        r = self.client.get("/api/v1/models/")
        self.assertEqual(r.data["results"][0]["developer_name"], "Anthropic")


class AIToolAPITest(APIAuthMixin, APITestCase):
    def test_list_returns_lightweight_serializer(self):
        make_tool()
        r = self.client.get("/api/v1/tools/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # List serializer should NOT include nested use_cases
        self.assertNotIn("use_cases", r.data["results"][0])

    def test_detail_returns_full_serializer(self):
        tool = make_tool()
        r = self.client.get(f"/api/v1/tools/{tool.pk}/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("use_cases", r.data)
        self.assertIn("attestations", r.data)
        self.assertIn("roles", r.data)

    def test_filter_by_approval_status(self):
        make_tool(name="Approved", approval_status="approved")
        make_tool(name="Pending", approval_status="pending")
        r = self.client.get("/api/v1/tools/?approval_status=approved")
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["name"], "Approved")

    def test_filter_by_deployment_type(self):
        make_tool(name="Cloud", deployment_type="cloud")
        make_tool(name="OnPrem", deployment_type="on_premise")
        r = self.client.get("/api/v1/tools/?deployment_type=cloud")
        self.assertEqual(r.data["count"], 1)

    def test_search_by_name(self):
        make_tool(name="GitHub Copilot")
        make_tool(name="MS Word")
        r = self.client.get("/api/v1/tools/?search=copilot")
        self.assertEqual(r.data["count"], 1)

    def test_update_approval_status(self):
        tool = make_tool(approval_status="pending")
        r = self.client.patch(f"/api/v1/tools/{tool.pk}/", {"approval_status": "approved"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        tool.refresh_from_db()
        self.assertEqual(tool.approval_status, "approved")


class UseCaseAPITest(APIAuthMixin, APITestCase):
    def test_list(self):
        make_use_case()
        r = self.client.get("/api/v1/usecases/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 1)

    def test_create(self):
        tool = make_tool()
        r = self.client.post("/api/v1/usecases/", {
            "title": "Summarise documents",
            "tools": [tool.pk],
            "risk_level": "medium",
            "autonomy_level": "human_in_loop",
            "human_in_loop": True,
            "is_public_facing": False,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_filter_by_risk_level(self):
        make_use_case(title="Low risk", risk_level="low")
        make_use_case(title="High risk", risk_level="high")
        r = self.client.get("/api/v1/usecases/?risk_level=high")
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["title"], "High risk")

    def test_nested_attestations_in_detail(self):
        tool = make_tool()
        uc = make_use_case(tool=tool)
        Attestation.objects.create(use_case=uc, attestation_type="dpia", status="completed")
        r = self.client.get(f"/api/v1/usecases/{uc.pk}/")
        self.assertEqual(len(r.data["attestations"]), 1)


class AttestationAPITest(APIAuthMixin, APITestCase):
    def test_create_on_tool(self):
        tool = make_tool()
        r = self.client.post("/api/v1/attestations/", {
            "tool": tool.pk,
            "attestation_type": "security",
            "status": "completed",
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_filter_by_status(self):
        make_attestation(status="completed")
        make_attestation(status="pending")
        r = self.client.get("/api/v1/attestations/?status=completed")
        self.assertEqual(r.data["count"], 1)


class RoleAPITest(APIAuthMixin, APITestCase):
    def test_create_sro(self):
        tool = make_tool()
        r = self.client.post("/api/v1/roles/", {
            "tool": tool.pk,
            "role_type": "sro",
            "person_name": "Jane Smith",
            "email": "jane@example.gov.uk",
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_filter_by_role_type(self):
        make_role(role_type="sro")
        make_role(role_type="dpo", person_name="Bob")
        r = self.client.get("/api/v1/roles/?role_type=sro")
        self.assertEqual(r.data["count"], 1)
