import asyncio
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
from .models import Parameter, ParameterFromAnalogSensorForBBO, ManagementConcentrationFlowForBBO, CommandForBBO, \
    Notification
from .serializers import ParameterFromAnalogSensorForBBOSerializer, BBOSerializer, \
    ManagementConcentrationFlowForBBOSerializer, CommandForBBOSerializer, NotificationSerializer


def data_func_for_notification():
    queryset = Notification.objects.all()
    data = []
    message_count = len(queryset)
    if message_count > 10:
        count = 10
    else:
        count = message_count
    for item in range(count):
        data.insert(item, queryset.order_by('-created_date')[item], )
    return data

def data_func_for_parameter():
    queryset = ParameterFromAnalogSensorForBBO.objects.all()
    data = []
    for item in range(27):
        data.insert(item, queryset.order_by('-time')[item], )
    return data

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
    queryset = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-pk').all()
    data = []
    for item in range(27):
        data.insert(item, queryset.order_by('-pk')[item], )
    permissions = (permissions.AllowAny,)


    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        loop = asyncio.get_event_loop()
        async_function = sync_to_async(data_func_for_parameter)
        ans = loop.create_task(async_function())
        await ans
        answer1 = dict(
            data=ParameterFromAnalogSensorForBBOSerializer(instance=ans.result(), many=True).data,
        )

        await self.send_json(answer1)

    @model_observer(ParameterFromAnalogSensorForBBO)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        # if action.value == 'create' and str(instance.bbo_id) == 'BBO1' and instance.name == 'valve_4':
        #     qs = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:12]
        #     return dict(bbo=f'{instance.bbo_id}', data=ParameterFromAnalogSensorForBBOSerializer(qs, many=True).data,
        #     )
        # if action.value == 'create' and str(instance.bbo_id) == 'BBO2' and instance.name == 'silt_level':
        #     qs = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2).order_by('-id')[:5]
        #     return dict(bbo=f'{instance.bbo_id}', data=ParameterFromAnalogSensorForBBOSerializer(qs, many=True).data,
        #     )
        # if action.value == 'create' and str(instance.bbo_id) == 'BBO3' and instance.name == 'silt_level':
        #     qs = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3).order_by('-id')[:5]
        #     return dict(bbo=f'{instance.bbo_id}', data=ParameterFromAnalogSensorForBBOSerializer(qs, many=True).data,
        #     )
        if action.value == 'create' and str(instance.bbo_id) == 'BBO4' and instance.name == 'silt_level':
            qs1 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:12]
            qs2 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2).order_by('-id')[:5]
            qs3 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3).order_by('-id')[:5]
            qs4 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=4).order_by('-id')[:5]
            return dict(
                bbo1=ParameterFromAnalogSensorForBBOSerializer(qs1, many=True).data,
                bbo2=ParameterFromAnalogSensorForBBOSerializer(qs2, many=True).data,
                bbo3=ParameterFromAnalogSensorForBBOSerializer(qs3, many=True).data,
                bbo4=ParameterFromAnalogSensorForBBOSerializer(qs4, many=True).data,
                )

# TODO веб сокет для отправки на клиент - надо написать, ниже тока шаблон как для аналогов
class CommandForBBOConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = CommandForBBOSerializer
    queryset = CommandForBBO.objects.all()
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        await self.send(text_data=json.dumps({
            'status': 'connected'
        }))

    @model_observer(CommandForBBO)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            qs = CommandForBBO.objects.filter(bbo_id=1).order_by('-id')[:9]
            return dict(data=CommandForBBOSerializer(qs, many=True).data,)



class NotificationConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permissions = (permissions.AllowAny,)


    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        loop = asyncio.get_event_loop()
        async_function = sync_to_async(data_func_for_notification)
        ans = loop.create_task(async_function())
        await ans
        answer1 = dict(
            data=NotificationSerializer(instance=ans.result(), many=True).data,
        )

        await self.send_json(answer1)


    @model_observer(Notification)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            # qs = Notification.objects.filter(bbo_id=1).order_by('-id')[:10]
            return dict(data=NotificationSerializer(instance, many=False).data,)