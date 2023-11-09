import json
from typing import Dict, Union, Any
from django.core import serializers
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer
from rest_framework.utils.serializer_helpers import ReturnDict

# from core.logic_for_bbo import AllParameterFromAnalogSensorForBBO1View
from .models import Parameter, ParameterFromAnalogSensorForBBO, ManagementConcentrationFlowForBBO
from .serializers import ParameterFromAnalogSensorForBBOSerializer, BBOSerializer, ManagementConcentrationFlowForBBOSerializer


class AirFlowConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = ManagementConcentrationFlowForBBOSerializer
    queryset = ManagementConcentrationFlowForBBO.objects.last()
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        answer = dict(data=ManagementConcentrationFlowForBBOSerializer(instance=AirFlowConsumer.queryset).data, )
        await self.send_json(
            answer
        )

    @model_observer(ManagementConcentrationFlowForBBO)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            return dict(data=ManagementConcentrationFlowForBBOSerializer(instance=instance).data, action=action.value, )



class ParameterConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = BBOSerializer
    queryset = ParameterFromAnalogSensorForBBO.objects.all()
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        await self.send(text_data=json.dumps({
            'status': 'connected'
        }))

    @model_observer(ParameterFromAnalogSensorForBBO)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create' and instance.name == 'valve_4':
            qs = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:12]
            return dict(bbo=f'{instance.bbo_id}', data=ParameterFromAnalogSensorForBBOSerializer(qs, many=True).data,
                        action=action.value, )

# TODO веб сокет для отправки на клиент - надо написать, ниже тока шаблон как для аналогов
# class AirManagerConsumer(ListModelMixin, GenericAsyncAPIConsumer):
#     serializer_class = BBOSerializer
#     queryset = ParameterFromAnalogSensorForBBO.objects.all()
#     permissions = (permissions.AllowAny,)
#
#     async def connect(self, **kwargs):
#         await self.model_change.subscribe()
#         await super().connect()
#         await self.send(text_data=json.dumps({
#             'status': 'connected'
#         }))
#
#     @model_observer(ParameterFromAnalogSensorForBBO)
#     async def model_change(self, message, observer=None, **kwargs):
#         if message:
#             await self.send_json(message)
#
#     @model_change.serializer
#     def model_serialize(self, instance, action, **kwargs):
#         if action.value == 'create' and instance.name == 'valve_4':
#             qs = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:9]
#             return dict(bbo=f'{instance.bbo_id}', data=ParameterFromAnalogSensorForBBOSerializer(qs, many=True).data,
#                         action=action.value, )