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
    Alert,
    AlertCriteria,
    AlertHistory,
    AlertState,
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


class AlertCriteriaInline(admin.TabularInline):
    model = AlertCriteria
    extra = 1


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("idAlert", "name", "is_active", "data_frequency", "duration")
    search_fields = ("name",)
    list_filter = ("is_active", "data_frequency")
    inlines = [AlertCriteriaInline]


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = ("machine", "alert", "triggered_at")
    list_filter = ("triggered_at", "alert")
    readonly_fields = ("machine", "alert", "triggered_at", "details", "contacts_notified")


@admin.register(AlertState)
class AlertStateAdmin(admin.ModelAdmin):
    list_display = ("alert", "machine", "current_status", "last_triggered_at")
    list_filter = ("current_status",)
    readonly_fields = ("alert", "machine", "last_triggered_at", "last_condition_met_at")


admin.site.register(AlertCriteria)
