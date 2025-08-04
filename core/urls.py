from django.urls import path

from core.views.user import register, login, user_list, user_detail, user_update, user_delete
from core.views.subsystem_status import get_post_subsystem_status, get_subsystem_status_detail, \
    update_subsystem_status, delete_subsystem_status
from core.views.system import get_post_system, get_system_detail, update_system, delete_system
from core.views.subsystem import get_post_subsystem, subsystem_detail, subsystems_by_system, subsystem_update, subsystem_delete

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/', user_list, name='user-list'),
    path('users/<int:user_id>/', user_detail, name='user-detail'),
    path('users/<int:user_id>/update/', user_update, name='user-update'),
    path('users/<int:user_id>/delete/', user_delete, name='user-delete'),

    path('subsystem_statuses/', get_post_subsystem_status, name='subsystem-status-get-post'),
    path('subsystem_statuses/<int:ss_status_id>/', get_subsystem_status_detail, name='subsystem-status-detail'),
    path('subsystem_statuses/<int:ss_status_id>/update/', update_subsystem_status, name='subsystem-status-update'),
    path('subsystem_statuses/<int:ss_status_id>/delete/', delete_subsystem_status, name='subsystem-status-delete'),

    path('systems/', get_post_system, name='system-get-post'),
    path('systems/<int:system_id>/', get_system_detail, name='system-detail'),
    path('systems/<int:system_id>/update/', update_system, name='system-update'),
    path('systems/<int:system_id>/delete/', delete_system, name='system-delete'),

    path('subsystems/', get_post_subsystem, name='get-post-subsystem'),
    path('subsystems/<int:subsystem_id>/', subsystem_detail, name='subsystem-detail'),
    path('subsystems/by-system/<int:system_id>/', subsystems_by_system, name='subsystems-by-system'),
    path('subsystems/<int:subsystem_id>/update/', subsystem_update, name='subsystem-update'),
    path('subsystems/<int:subsystem_id>/delete/', subsystem_delete, name='subsystem-delete'),
]
