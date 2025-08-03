from django.urls import path
from core.views.subsystem_status import SubsystemStatusCRUD
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from core.drfutil.async_spectacular import AsyncSpectacularAPIView  # Импортируй новый класс

urlpatterns = [
    path('subsystem_status/', SubsystemStatusCRUD.as_view(), name='subsystem-status-crud'),
    path('schema/', AsyncSpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]