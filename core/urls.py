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
from core.views.attachment import get_post_attachment, attachment_detail, attachment_download, attachment_delete
from core.views.category import get_post_category, get_category_detail, update_category, delete_category
from core.views.location_type import get_post_location_type, get_location_type_detail, update_location_type, delete_location_type
from core.views.region import get_post_region, get_region_detail, update_region, delete_region

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

    path('attachments/', get_post_attachment, name='attachment-get-post'),
    path('attachments/<int:attachment_id>/', attachment_detail, name='attachment-detail'),
    path('attachments/<int:attachment_id>/download/', attachment_download, name='attachment-download'),
    path('attachments/<int:attachment_id>/delete/', attachment_delete, name='attachment-delete'),

    path('categories/', get_post_category, name='category-get-post'),
    path('categories/<int:category_id>/', get_category_detail, name='category-detail'),
    path('categories/<int:category_id>/update/', update_category, name='category-update'),
    path('categories/<int:category_id>/delete/', delete_category, name='category-delete'),

    path('location_types/', get_post_location_type, name='location-type-get-post'),
    path('location_types/<int:location_type_id>/', get_location_type_detail, name='location-type-detail'),
    path('location_types/<int:location_type_id>/update/', update_location_type, name='location-type-update'),
    path('location_types/<int:location_type_id>/delete/', delete_location_type, name='location-type-delete'),

    path('regions/', get_post_region, name='region-get-post'),
    path('regions/<int:region_id>/', get_region_detail, name='region-detail'),
    path('regions/<int:region_id>/update/', update_region, name='region-update'),
    path('regions/<int:region_id>/delete/', delete_region, name='region-delete'),
]
