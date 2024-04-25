from django.urls import path, re_path
from rest_framework_swagger.views import get_swagger_view

from . import views, logic_for_bbo
from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .logic_for_bbo import (
    PostLabValueView,
    GetLabValueView,
    PostProjValueView,
    GetProjValueView,
    GetAllBBOProjValueView,
    GetAllBBOLabValueView,
    ParameterFromAnalogSensorForBBOView, AllParameterFromAnalogSensorForBBO1View,
    AirManagerView, CommandForBBOView, stat_detail, ManagementRecycleForBBOView, ManagementVolumeFlowForBBOView,
    WorkModeView, GetDatesForLabValue, GetLabValueFromDates, GetLabValueFromID, UpdateLabValueByID,
    NotificationManagerView, DistributionBowlView
)


schema_view = get_swagger_view(title='WWTP API')

urlpatterns = [
    path('post_lab_value', PostLabValueView.as_view()),
    # path('get_lab_value', GetLabValueView.as_view()),
    # path('get_proj_value', GetProjValueView.as_view()),
    path('post_proj_value', PostProjValueView.as_view()),
    path('get_all_proj_value', GetAllBBOProjValueView.as_view()),
    path('get_all_lab_value', GetAllBBOLabValueView.as_view()),
    path('get_dates', GetDatesForLabValue.as_view()),
    re_path(r'get_lab_from_dates', GetLabValueFromDates.as_view()),
    re_path(r'get_lab_from_id', GetLabValueFromID.as_view()),
    re_path(r'^update_lab_val/(?P<lab_id>[0-9]+)$', UpdateLabValueByID.as_view()),
    path('post_analog_parameter', ParameterFromAnalogSensorForBBOView.as_view()),
    path('get_manager_air_flow', AirManagerView.as_view()),
    path('post_manager_air_flow', AirManagerView.as_view()),
    path('post_command', CommandForBBOView.as_view()),
    path('recycle', ManagementRecycleForBBOView.as_view()),
    path('manager_volume_flow', ManagementVolumeFlowForBBOView.as_view()),
    path('change_mode', WorkModeView.as_view()),
    path('sensor_borders', NotificationManagerView.as_view()),
    path('bowl', DistributionBowlView.as_view()),
    path('swagger', schema_view),
    re_path(r'stat', logic_for_bbo.stat_detail),
    # re_path(r'stat/(?P<bbo_id>.+)/(?P<name>.+)/(?P<first_date>.+)/(?P<last_date>.+)$', logic_for_bbo.stat_detail),

]