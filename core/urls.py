from django.urls import path

from core.views.user import register, login, user_list, user_detail, user_update, user_delete
from core.views.subsystem_status import get_post_subsystem_status, get_subsystem_status_detail, \
    update_subsystem_status, delete_subsystem_status
from core.views.system import get_post_system, get_system_detail, update_system, delete_system
from core.views.subsystem import get_post_subsystem, subsystem_detail, subsystems_by_system, subsystem_update, \
    subsystem_delete
from core.views.condition import get_post_condition, get_condition_detail, update_condition, delete_condition
from core.views.precipitation import get_post_precipitation, get_precipitation_detail, update_precipitation, \
    delete_precipitation
from core.views.source import get_post_source, get_source_detail, update_source, delete_source

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

    path('conditions/', get_post_condition, name='condition-get-post'),
    path('conditions/<int:condition_id>/', get_condition_detail, name='condition-detail'),
    path('conditions/<int:condition_id>/update/', update_condition, name='condition-update'),
    path('conditions/<int:condition_id>/delete/', delete_condition, name='condition-delete'),

    path('precipitations/', get_post_precipitation, name='precipitation-get-post'),
    path('precipitations/<int:precipitation_id>/', get_precipitation_detail, name='precipitation-detail'),
    path('precipitations/<int:precipitation_id>/update/', update_precipitation, name='precipitation-update'),
    path('precipitations/<int:precipitation_id>/delete/', delete_precipitation, name='precipitation-delete'),

    path('sources/', get_post_source, name='source-get-post'),
    path('sources/<int:source_id>/', get_source_detail, name='source-detail'),
    path('sources/<int:source_id>/update/', update_source, name='source-update'),
    path('sources/<int:source_id>/delete/', delete_source, name='source-delete'),
]
