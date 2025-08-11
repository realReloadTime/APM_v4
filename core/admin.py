from core.models import *
from django.contrib.admin import AdminSite


custom_admin_site = AdminSite(name='custom_admin')

for model in [
    SubsystemStatus, System, Subsystem,
    Condition, Precipitation, Source,
    Attachment, Category,
    LocationType, Region, LOA,
    Location, ObjectType, Object,
    Event, MeasuresTaken, EquipmentFailure,
    AdverseWeather, FireDanger, GeologicalDanger,
    HydrologicalDanger, EmergencySituation, OtherDanger, CustomUser
]:
    custom_admin_site.register(model)