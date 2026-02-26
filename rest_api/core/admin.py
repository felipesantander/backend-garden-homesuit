from django.contrib import admin
from core.models import (
    Business,
    Channel,
    ConfigurationChannel,
    Data,
    Garden,
    Machine,
    MachineCandidate,
    Notification,
    Permission,
    Role,
    UserRole,
)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("idChannel", "name", "unit", "color", "icon", "business")
    search_fields = ("name", "idChannel")


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("machineId", "serial", "Name", "garden")
    search_fields = ("serial", "Name", "machineId")


@admin.register(Garden)
class GardenAdmin(admin.ModelAdmin):
    list_display = ("idGarden", "name", "business")
    search_fields = ("name", "idGarden")


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("idBusiness", "name")
    search_fields = ("name", "idBusiness")


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ("idData", "machineId", "channelId", "type", "base_date", "count")
    search_fields = ("machineId__serial", "channelId__name")


admin.site.register(ConfigurationChannel)
admin.site.register(MachineCandidate)
admin.site.register(Notification)
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(UserRole)
