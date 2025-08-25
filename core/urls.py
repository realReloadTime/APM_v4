from django.urls import path

from core.views.user import register, login, refresh_auth_token, user_list, user_detail, user_update, user_delete, get_user_self
from core.views.subsystem_status import get_post_subsystem_status, get_subsystem_status_detail, \
    update_subsystem_status, delete_subsystem_status
from core.views.system import get_post_system, get_system_detail, update_system, delete_system
from core.views.subsystem import get_post_subsystem, subsystem_detail, subsystems_by_system, subsystem_update, \
    subsystem_delete
from core.views.condition import get_post_condition, get_condition_detail, update_condition, delete_condition
from core.views.precipitation import get_post_precipitation, get_precipitation_detail, update_precipitation, \
    delete_precipitation
from core.views.source import get_post_source, get_source_detail, update_source, delete_source
from core.views.attachment import get_post_attachment, attachment_detail, attachment_download, attachment_update, \
    attachment_delete
from core.views.category import get_post_category, get_category_detail, update_category, delete_category
from core.views.location_type import get_post_location_type, get_location_type_detail, update_location_type, \
    delete_location_type
from core.views.region import get_post_region, get_region_detail, update_region, delete_region
from core.views.loa import get_post_loa, loa_detail, loas_by_region, loa_update, loa_delete
from core.views.location import get_post_location, location_detail, location_update, location_delete, location_by_loa_id
from core.views.object_type import get_post_object_type, get_object_type_detail, update_object_type, delete_object_type
from core.views.object import get_post_object, object_detail, object_update, object_delete
from core.views.measures_taken import get_post_measures_taken, get_measures_taken_detail, get_measures_taken_by_event, update_measures_taken, \
    delete_measures_taken
from core.views.event import get_post_event, get_event_detail, update_event, delete_event
from core.views.equipment_failure import get_post_equipment_failure, get_equipment_failure_detail, \
    update_equipment_failure, delete_equipment_failure, equipment_failure_by_event
from core.views.adverse_weather import get_post_adverse_weather, get_adverse_weather_detail, \
    adverse_weather_by_event, update_adverse_weather, delete_adverse_weather
from core.views.fire_danger import get_post_fire_danger, get_fire_danger_detail, fire_danger_by_event, \
    update_fire_danger, delete_fire_danger
from core.views.geological_danger import get_post_geological_danger, get_geological_danger_detail, \
    geological_danger_by_event, update_geological_danger, delete_geological_danger
from core.views.hydrological_danger import get_post_hydrological_danger, get_hydrological_danger_detail, \
    hydrological_danger_by_event, update_hydrological_danger, delete_hydrological_danger
from core.views.emergency_situation import get_post_emergency_situation, get_emergency_situation_detail, \
    emergency_situation_by_event, update_emergency_situation, delete_emergency_situation
from core.views.other_danger import get_post_other_danger, get_other_danger_detail, other_danger_by_event, \
    update_other_danger, delete_other_danger
from core.views.report import download_report

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh_token/', refresh_auth_token, name='refresh'),
    path('users/', user_list, name='user-list'),
    path('users/me/', get_user_self, name='user_self'),
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
    path('attachments/<int:attachment_id>/update/', attachment_update, name='attachment-update'),
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

    path('loas/', get_post_loa, name='get-post-loa'),
    path('loas/<int:loa_id>/', loa_detail, name='loa-detail'),
    path('loas/by-region/<int:region_id>/', loas_by_region, name='loas-by-region'),
    path('loas/<int:loa_id>/update/', loa_update, name='loa-update'),
    path('loas/<int:loa_id>/delete/', loa_delete, name='loa-delete'),

    path('locations/', get_post_location, name='get-post-location'),
    path('locations/<int:location_id>/', location_detail, name='location-detail'),
    path('locations/by-loa/<int:loa_id>/', location_by_loa_id, name='location-by-loa'),
    path('locations/<int:location_id>/update/', location_update, name='location-update'),
    path('locations/<int:location_id>/delete/', location_delete, name='location-delete'),

    path('object_types/', get_post_object_type, name='object_type-get-post'),
    path('object_types/<int:object_type_id>/', get_object_type_detail, name='object_type-detail'),
    path('object_types/<int:object_type_id>/update/', update_object_type, name='object_type-update'),
    path('object_types/<int:object_type_id>/delete/', delete_object_type, name='object_type-delete'),

    path('objects/', get_post_object, name='get-post-object'),
    path('objects/<int:object_id>/', object_detail, name='object-detail'),
    path('objects/<int:object_id>/update/', object_update, name='object-update'),
    path('objects/<int:object_id>/delete/', object_delete, name='object-delete'),

    path('measures/', get_post_measures_taken, name='measures_taken-get-post'),
    path('measures/<int:measures_taken_id>/', get_measures_taken_detail, name='measures_taken-detail'),
    path('measures/by-event/<int:event_id>/', get_measures_taken_by_event, name='measures_taken-by-event'),
    path('measures/<int:measures_taken_id>/update/', update_measures_taken, name='measures_taken-update'),
    path('measures/<int:measures_taken_id>/delete/', delete_measures_taken, name='measures_taken-delete'),

    path('events/', get_post_event, name='event-get-post'),
    path('events/<int:event_id>/', get_event_detail, name='event-detail'),
    path('events/<int:event_id>/update/', update_event, name='event-update'),
    path('events/<int:event_id>/delete/', delete_event, name='event-delete'),

    path('equipment_failures/', get_post_equipment_failure, name='equipment_failure-get-post'),
    path('equipment_failures/<int:failure_id>/', get_equipment_failure_detail, name='equipment_failure-detail'),
    path('equipment_failures/by-event/<int:event_id>/', equipment_failure_by_event,
         name='equipment_failure-by-event'),
    path('equipment_failures/<int:failure_id>/update/', update_equipment_failure, name='equipment_failure-update'),
    path('equipment_failures/<int:failure_id>/delete/', delete_equipment_failure, name='equipment_failure-delete'),

    path('adverse_weathers/', get_post_adverse_weather, name='adverse_weather-get-post'),
    path('adverse_weathers/<int:weather_id>/', get_adverse_weather_detail, name='adverse_weather-detail'),
    path('adverse_weathers/by-event/<int:event_id>/', adverse_weather_by_event,
         name='adverse_weather-by-event'),
    path('adverse_weathers/<int:weather_id>/update/', update_adverse_weather, name='adverse_weather-update'),
    path('adverse_weathers/<int:weather_id>/delete/', delete_adverse_weather, name='adverse_weather-delete'),

    path('fire_dangers/', get_post_fire_danger, name='fire_danger-get-post'),
    path('fire_dangers/<int:fire_id>/', get_fire_danger_detail, name='fire_danger-detail'),
    path('fire_dangers/by-event/<int:event_id>/', fire_danger_by_event,
         name='fire_danger-by-event'),
    path('fire_dangers/<int:fire_id>/update/', update_fire_danger, name='fire_danger-update'),
    path('fire_dangers/<int:fire_id>/delete/', delete_fire_danger, name='fire_danger-delete'),

    path('geological_dangers/', get_post_geological_danger, name='geological_danger-get-post'),
    path('geological_dangers/<int:geo_id>/', get_geological_danger_detail, name='geological_danger-detail'),
    path('geological_dangers/by-event/<int:event_id>/', geological_danger_by_event,
         name='geological_danger-by-event'),
    path('geological_dangers/<int:geo_id>/update/', update_geological_danger, name='geological_danger-update'),
    path('geological_dangers/<int:geo_id>/delete/', delete_geological_danger, name='geological_danger-delete'),

    path('hydrological_dangers/', get_post_hydrological_danger, name='hydrological_danger-get-post'),
    path('hydrological_dangers/<int:hydro_id>/', get_hydrological_danger_detail, name='hydrological_danger-detail'),
    path('hydrological_dangers/by-event/<int:event_id>/', hydrological_danger_by_event,
         name='hydrological_danger-by-event'),
    path('hydrological_dangers/<int:hydro_id>/update/', update_hydrological_danger, name='hydrological_danger-update'),
    path('hydrological_dangers/<int:hydro_id>/delete/', delete_hydrological_danger, name='hydrological_danger-delete'),

    path('emergency_situations/', get_post_emergency_situation, name='emergency_situation-get-post'),
    path('emergency_situations/<int:situation_id>/', get_emergency_situation_detail, name='emergency_situation-detail'),
    path('emergency_situations/by-event/<int:event_id>/', emergency_situation_by_event,
         name='emergency_situation-by-event'),
    path('emergency_situations/<int:situation_id>/update/', update_emergency_situation,
         name='emergency_situation-update'),
    path('emergency_situations/<int:situation_id>/delete/', delete_emergency_situation,
         name='emergency_situation-delete'),

    path('other_dangers/', get_post_other_danger, name='other_danger-get-post'),
    path('other_dangers/<int:danger_id>/', get_other_danger_detail, name='other_danger-detail'),
    path('other_dangers/by-event/<int:event_id>/', other_danger_by_event,
         name='other_danger-by-event'),
    path('other_dangers/<int:danger_id>/update/', update_other_danger, name='other_danger-update'),
    path('other_dangers/<int:danger_id>/delete/', delete_other_danger, name='other_danger-delete'),

    path('report/', download_report, name='download-report')
]
