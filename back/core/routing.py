from django.urls import re_path 
from . import consumers

websocket_urlpatterns = [
    re_path('ws/socket-server/', consumers.ParameterConsumer.as_asgi()),
    re_path('ws/air-flow/', consumers.AirFlowConsumer.as_asgi()),
    re_path('ws/command/', consumers.CommandForBBOConsumer.as_asgi()),
    re_path('ws/notification/', consumers.NotificationConsumer.as_asgi()),
]