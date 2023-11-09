from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from . import views
from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .logic_for_bbo import (
    PostLabValueView,
    GetLabValueView,
    PostProjValueView,
    GetProjValueView,
    GetAllBBOProjValueView,
    GetAllBBOLabValueView,
    ParameterFromAnalogSensorForBBOView, AllParameterFromAnalogSensorForBBO1View, AirManagerView
)

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('post_lab_value', PostLabValueView.as_view()),
    # path('get_lab_value', GetLabValueView.as_view()),
    # path('get_proj_value', GetProjValueView.as_view()),
    path('post_proj_value', PostProjValueView.as_view()),
    path('get_all_proj_value', GetAllBBOProjValueView.as_view()),
    path('get_all_lab_value', GetAllBBOLabValueView.as_view()),
    path('post_analog_parameter', ParameterFromAnalogSensorForBBOView.as_view()),
    path('get_manager_air_flow', AirManagerView.as_view()),
    path('post_manager_air_flow', AirManagerView.as_view()),
    path('swagger', schema_view),

]