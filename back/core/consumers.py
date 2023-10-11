import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer

from .models import Parameter
from .serializers import ParameterSerializer

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_group_name = 'test'
#
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         self.accept()
#         self.send(text_data=json.dumps({
#             'status':'connected'
#         }))
#
#
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type':'chat_message',
#                 'message':message
#             }
#         )
#
#     def chat_message(self, event):
#         message = event['message']
#
#         self.send(text_data=json.dumps({
#             'type':'back',
#             'message':message
#         }))


class ParameterConsumer(ListModelMixin, GenericAsyncAPIConsumer):

    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        await self.send(text_data=json.dumps({
            'status': 'connected'
        }))

    @model_observer(Parameter)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            return dict(data=ParameterSerializer(instance=instance).data, action=action.value)
