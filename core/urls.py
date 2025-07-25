from django.urls import path
from core.views.subsystem_status import SubsystemStatusCRUD
from core.admin import custom_admin_site
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('subsystem_status/', SubsystemStatusCRUD.as_view(), name='subsystem-status-crud'),
]