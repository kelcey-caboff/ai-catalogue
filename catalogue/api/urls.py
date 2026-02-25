from rest_framework.routers import DefaultRouter
from .views import (
    OrganisationViewSet,
    AIModelViewSet,
    AIToolViewSet,
    UseCaseViewSet,
    AttestationViewSet,
    RoleViewSet,
)

router = DefaultRouter()
router.register(r"organisations", OrganisationViewSet)
router.register(r"models", AIModelViewSet)
router.register(r"tools", AIToolViewSet)
router.register(r"usecases", UseCaseViewSet)
router.register(r"attestations", AttestationViewSet)
router.register(r"roles", RoleViewSet)

urlpatterns = router.urls
