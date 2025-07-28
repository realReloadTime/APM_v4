from django.contrib import admin
from .models import *
from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = "APM System Administration"
    site_title = "APM Admin Portal"
    index_title = "Добро пожаловать в систему управления APM"


custom_admin_site = CustomAdminSite(name='custom_admin')

for model in [
    SubsystemStatus, System, Subsystem,
    Condition, Precipitation, Source,
    User, Attachment, Category,
    LocationType, Region, LOA,
    Location, ObjectType, Object,
    Event, MeasuresTaken, EquipmentFailure,
    AdverseWeather, FireDanger, GeologicalDanger,
    HydrologicalDanger, EmergencySituation, OtherDanger, Token
]:
    custom_admin_site.register(model)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'begin', 'loa', 'category', 'location')
    list_filter = ('category', 'loa')
    search_fields = ('consequences', 'note')
    date_hierarchy = 'begin'
    raw_id_fields = ('attachments',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'read', 'edit', 'admin', 'created_at')
    list_editable = ('read', 'edit', 'admin')
    actions = ['make_admin']

    @admin.action(description='Дать права администратора')
    def make_admin(self, request, queryset):
        queryset.update(admin=True)


@admin.register(EquipmentFailure)
class EquipmentFailureAdmin(admin.ModelAdmin):
    list_display = ('event', 'object', 'subsystem_status')
    raw_id_fields = ('influenced_objects',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at'] if hasattr(model, 'created_at') else ['__str__']
    list_per_page = 50
    search_fields = ['name'] if hasattr(model, 'name') else []

    def get_list_display(self, request):
        base_list = super().get_list_display(request)

        return base_list + [f.name for f in self.model._meta.fields
                            if f.name not in base_list and f.name != 'id']
