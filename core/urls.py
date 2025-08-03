from django.urls import path
from core.views.subsystem_status import SubsystemStatusCRUD


urlpatterns = [
    path('subsystem_status/', SubsystemStatusCRUD.as_view(), name='subsystem-status-crud'),
]