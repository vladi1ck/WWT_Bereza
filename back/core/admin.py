from django.contrib.auth.admin import UserAdmin
from .models import User, BBO, Parameter, LabValue, ProjValue, ParameterFromAnalogSensorForBBO, \
    ManagementConcentrationFlowForBBO, CommandForBBO, Notification, ManagementRecycleForBBO, ManagementVolumeFlowForBBO
from django.contrib import admin


class MyUserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username',)  # Contain only fields in your `custom-user-model`
    list_filter = ()  # Contain only fields in your `custom-user-model` intended for filtering. Do not include `groups`since you do not have it
    readonly_fields = ["date_joined", ]
    exclude = ()
    search_fields = ()  # Contain only fields in your `custom-user-model` intended for searching
    ordering = ()  # Contain only fields in your `custom-user-model` intended to ordering
    filter_horizontal = ()  # Leave it empty. You have neither `groups` or `user_permissions`
    # fieldsets = UserAdmin.fieldsets + (
    #         (None, {'fields': ('mobile',)}),
    # )


@admin.register(BBO)
class MyBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'modified_by',)


@admin.register(ManagementRecycleForBBO)
class MyBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'time')


@admin.register(ProjValue)
class MyProjAdmin(admin.ModelAdmin):
    list_display = ('bbo_id', 'modified_time', 'modified_by')


@admin.register(LabValue)
class MyLabAdmin(admin.ModelAdmin):
    list_display = ('bbo_id', 'modified_time', 'modified_by')


@admin.register(ParameterFromAnalogSensorForBBO)
class MyParameterFromAnalogSensorForBBOAdmin(admin.ModelAdmin):
    list_display = ('rus_name', 'bbo_id', 'time')


@admin.register(ManagementConcentrationFlowForBBO)
class MyManagementAirFlowForBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'bbo_id', 'time')


@admin.register(ManagementVolumeFlowForBBO)
class ManagementVolumeFlowForBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'bbo_id', 'time')


@admin.register(CommandForBBO)
class MyCommandForBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'command', 'time', 'bbo_id',)


@admin.register(Notification)
class MyNotificationAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'status_code', 'bbo_id', 'message')


admin.site.register(User, MyUserAdmin)
admin.site.register(Parameter)
