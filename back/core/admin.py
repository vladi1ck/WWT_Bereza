from django.contrib.auth.admin import UserAdmin
from .models import User, BBO, Parameter, LabValue, ProjValue, ParameterFromAnalogSensorForBBO, ManagementConcentrationFlowForBBO
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


@admin.register(ProjValue)
class MyProjAdmin(admin.ModelAdmin):
    list_display = ('bbo_id', 'modified_time', 'modified_by')


@admin.register(LabValue)
class MyLabAdmin(admin.ModelAdmin):
    list_display = ('bbo_id', 'modified_time', 'modified_by')


@admin.register(ParameterFromAnalogSensorForBBO)
class MyParameterFromAnalogSensorForBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'bbo_id', 'time')

@admin.register(ManagementConcentrationFlowForBBO)
class MyManagementAirFlowForBBOAdmin(admin.ModelAdmin):
    list_display = ('name', 'bbo_id',)


admin.site.register(User, MyUserAdmin)
admin.site.register(Parameter)
