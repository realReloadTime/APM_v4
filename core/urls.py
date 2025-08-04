from django.urls import path
from core.views.user import register, login, user_list, user_detail, user_update, user_delete
from core.views.subsystem_status import get_subsystem_status_list, get_subsystem_status_detail, \
    update_subsystem_status, delete_subsystem_status

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/', user_list, name='user-list'),
    path('users/<int:user_id>/', user_detail, name='user-detail'),
    path('users/<int:user_id>/update/', user_update, name='user-update'),
    path('users/<int:user_id>/delete/', user_delete, name='user-delete'),

    path('subsystem_statuses/', get_subsystem_status_list, name='subsystem-status-list'),
    path('subsystem_statuses/<int:ss_status_id>/', get_subsystem_status_detail, name='subsystem-status-detail'),
    path('subsystem_statuses/<int:ss_status_id>/update/', update_subsystem_status, name='subsystem-status-update'),
    path('subsystem_statuses/<int:ss_status_id>/delete/', delete_subsystem_status, name='subsystem-status-delete'),
]
