from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("tools/", views.ToolListView.as_view(), name="tool-list"),
    path("tools/<int:pk>/", views.ToolDetailView.as_view(), name="tool-detail"),
    path("models/", views.ModelListView.as_view(), name="model-list"),
    path("models/<int:pk>/", views.ModelDetailView.as_view(), name="model-detail"),
    path("use-cases/", views.UseCaseListView.as_view(), name="usecase-list"),
    path("use-cases/<int:pk>/", views.UseCaseDetailView.as_view(), name="usecase-detail"),
    # Focused views
    path("assured/", views.AssuredToolsView.as_view(), name="assured"),
    path("horizon/", views.HorizonView.as_view(), name="horizon"),
    path("by-department/", views.ByDepartmentView.as_view(), name="by-department"),
    path("model-map/", views.ModelMapView.as_view(), name="model-map"),
]
