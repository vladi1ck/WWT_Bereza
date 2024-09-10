import asyncio
import datetime
import json
from typing import Dict, Union, Any

import channels.db
from django.core import serializers
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Max
from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer
from rest_framework.utils.serializer_helpers import ReturnDict

# from core.logic_for_bbo import AllParameterFromAnalogSensorForBBO1View
from .models import Parameter, ParameterFromAnalogSensorForBBO, ManagementConcentrationFlowForBBO, CommandForBBO, \
    Notification, ManagementVolumeFlowForBBO, WorkMode, DistributionBowl, Diffusor, SiltPumpStation, WorkSettingsSingle
from .serializers import ParameterFromAnalogSensorForBBOSerializer, BBOSerializer, \
    ManagementConcentrationFlowForBBOSerializer, CommandForBBOSerializer, NotificationSerializer, \
    ManagementVolumeFlowForBBOSerializer, WorkModeSerializer, HPKSerializer, DistributionBowlSerializer, \
    DiffusorSerializer, SiltPumpStationSerializer, WorkSettingsSingleSerializer


def data_func_for_notification():
    qs = Notification.objects.all().order_by('-pk')[:10]
    return NotificationSerializer(qs, many=True).data


@channels.db.database_sync_to_async
def change_notify(pk, is_read):
    try:
        read_time = str(datetime.datetime.now())
        qs = Notification.objects.filter(pk=pk).update(is_read=is_read, read_time=read_time)
        return NotificationSerializer(qs, many=False).data
    except Exception as _ex:
        print(_ex)


def data_func_for_work_mode():
    qs = WorkMode.objects.last()
    return WorkModeSerializer(qs, many=False).data


def data_func_for_parameter():
    qs1 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:12]
    qs2 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2).order_by('-id')[:11]
    qs3 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3).order_by('-id')[:11]
    qs4 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=4).order_by('-id')[:11]
    qs5 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=5).order_by('-id')[:7]
    conc1 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=1).last()
    conc2 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=2).last()
    conc3 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=3).last()
    conc4 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=4).last()
    qs6 = ManagementVolumeFlowForBBO.objects.last()
    mode = WorkMode.objects.last()
    bowl1 = DistributionBowl.objects.filter(bbo_id=1).last()
    bowl2 = DistributionBowl.objects.filter(bbo_id=2).last()
    bowl3 = DistributionBowl.objects.filter(bbo_id=3).last()
    bowl4 = DistributionBowl.objects.filter(bbo_id=4).last()
    diffusor = Diffusor.objects.last()
    silt_state = SiltPumpStation.objects.last()
    avg_oxy_state = WorkSettingsSingle.objects.filter(id=1).last()
    oxygen_1_1_state = WorkSettingsSingle.objects.filter(id=2).last()
    oxygen_1_2_state = WorkSettingsSingle.objects.filter(id=3).last()
    oxygen_1_3_state = WorkSettingsSingle.objects.filter(id=4).last()
    oxygen_1_4_state = WorkSettingsSingle.objects.filter(id=5).last()

    water_consumption_in = ParameterFromAnalogSensorForBBO.objects.filter(name='water_consumption_in').first()
    air_supply = ParameterFromAnalogSensorForBBO.objects.filter(name='air_supply').first()
    current_air_consumption = air_supply.value / water_consumption_in.value

    sum = 0
    res = 0
    hpk_today = (ParameterFromAnalogSensorForBBO.objects.filter(name='HPK',
                                                                time__range=[
                                                                    f'{datetime.datetime.today().date()} 00:00:00',
                                                                    f'{datetime.datetime.today().date()} 23:59:59'])
                 .all())
    for val in hpk_today:
        sum = sum + val.value
        try:
            res = round(sum / len(hpk_today), 2)
        except Exception as _ex:
            print(_ex)
            res = 0
    max_value = ParameterFromAnalogSensorForBBO.objects.filter(name='HPK',
                                                               time__range=[
                                                                   f'{datetime.datetime.today().date()} 00:00:00',
                                                                   f'{datetime.datetime.today().date()} 23:59:59']).aggregate(
        Max('value'))
    if max_value['value__max'] is None:
        max_value['value__max'] = 0
    avg_HPK_today = res
    avg_HPK_yesterday = None
    max_HPK_yesterday = None
    try:
        avg_HPK_yesterday = ParameterFromAnalogSensorForBBO.objects.filter(name='avg_HPK_yesterday').first()
        max_HPK_yesterday = ParameterFromAnalogSensorForBBO.objects.filter(name='max_HPK_yesterday').first()
    except Exception as _ex:
        print(_ex)
        avg_HPK_yesterday = 0
        max_HPK_yesterday = 0
    return dict(
        bbo1=ParameterFromAnalogSensorForBBOSerializer(qs1, many=True).data,
        bbo2=ParameterFromAnalogSensorForBBOSerializer(qs2, many=True).data,
        bbo3=ParameterFromAnalogSensorForBBOSerializer(qs3, many=True).data,
        bbo4=ParameterFromAnalogSensorForBBOSerializer(qs4, many=True).data,
        common=ParameterFromAnalogSensorForBBOSerializer(qs5, many=True).data,
        air_flow_volume=ManagementVolumeFlowForBBOSerializer(qs6, many=False).data,
        air_concentration1=ManagementConcentrationFlowForBBOSerializer(conc1, many=False).data,
        air_concentration2=ManagementConcentrationFlowForBBOSerializer(conc2, many=False).data,
        air_concentration3=ManagementConcentrationFlowForBBOSerializer(conc3, many=False).data,
        air_concentration4=ManagementConcentrationFlowForBBOSerializer(conc4, many=False).data,
        work_mode=WorkModeSerializer(mode, many=False).data,
        avg_hpk_today=avg_HPK_today,
        max_hpk_today=round(max_value['value__max'], 2),
        avg_hpk_yesterday=HPKSerializer(avg_HPK_yesterday, many=False).data,
        max_hpk_yesterday=HPKSerializer(max_HPK_yesterday, many=False).data,
        bowl1=DistributionBowlSerializer(bowl1, many=False).data,
        bowl2=DistributionBowlSerializer(bowl2, many=False).data,
        bowl3=DistributionBowlSerializer(bowl3, many=False).data,
        bowl4=DistributionBowlSerializer(bowl4, many=False).data,
        current_air_consumption=round(current_air_consumption, 2),
        diffusor=DiffusorSerializer(diffusor, many=False).data,
        silt_pump_state=SiltPumpStationSerializer(silt_state, many=False).data,
        avg_oxy_state=WorkSettingsSingleSerializer(avg_oxy_state, many=False).data,
        oxygen_1_1_state=WorkSettingsSingleSerializer(oxygen_1_1_state, many=False).data,
        oxygen_1_2_state=WorkSettingsSingleSerializer(oxygen_1_2_state, many=False).data,
        oxygen_1_3_state=WorkSettingsSingleSerializer(oxygen_1_3_state, many=False).data,
        oxygen_1_4_state=WorkSettingsSingleSerializer(oxygen_1_4_state, many=False).data,
    )
    # queryset = ParameterFromAnalogSensorForBBO.objects.all()
    # data = []
    # for item in range(27):
    #     data.insert(item, queryset.order_by('-time')[item], )
    # return data


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
    # queryset = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-pk').all()
    # data = []
    # for item in range(27):
    #     data.insert(item, queryset.order_by('-pk')[item], )
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        loop = asyncio.get_event_loop()
        async_function = sync_to_async(data_func_for_parameter)
        ans = loop.create_task(async_function())
        await ans
        # answer1 = dict(
        #     data=ParameterFromAnalogSensorForBBOSerializer(instance=ans.result(), many=True).data,
        # )

        await self.send_json(ans.result())

    @model_observer(ParameterFromAnalogSensorForBBO)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create' and str(instance.bbo_id) == 'Common' and instance.name == 'air_supply':
            qs1 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1).order_by('-id')[:12]
            qs2 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2).order_by('-id')[:11]
            qs3 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3).order_by('-id')[:11]
            qs4 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=4).order_by('-id')[:11]
            qs5 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=5).order_by('-id')[:7]
            qs6 = ManagementVolumeFlowForBBO.objects.last()
            conc1 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=1).last()
            conc2 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=2).last()
            conc3 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=3).last()
            conc4 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=4).last()
            mode = WorkMode.objects.last()
            bowl1 = DistributionBowl.objects.filter(bbo_id=1).last()
            bowl2 = DistributionBowl.objects.filter(bbo_id=2).last()
            bowl3 = DistributionBowl.objects.filter(bbo_id=3).last()
            bowl4 = DistributionBowl.objects.filter(bbo_id=4).last()
            diffusor = Diffusor.objects.last()
            silt_state = SiltPumpStation.objects.last()
            avg_oxy_state = WorkSettingsSingle.objects.filter(id=1).last()
            oxygen_1_1_state = WorkSettingsSingle.objects.filter(id=2).last()
            oxygen_1_2_state = WorkSettingsSingle.objects.filter(id=3).last()
            oxygen_1_3_state = WorkSettingsSingle.objects.filter(id=4).last()
            oxygen_1_4_state = WorkSettingsSingle.objects.filter(id=5).last()

            water_consumption_in = ParameterFromAnalogSensorForBBO.objects.filter(name='water_consumption_in').first()
            air_supply = ParameterFromAnalogSensorForBBO.objects.filter(name='air_supply').first()
            current_air_consumption = air_supply.value / water_consumption_in.value

            sum = 0
            res = 0
            hpk_today = (ParameterFromAnalogSensorForBBO.objects.filter(name='HPK',
                                                                        time__range=[
                                                                            f'{datetime.datetime.today().date()} 00:00:00',
                                                                            f'{datetime.datetime.today().date()} 23:59:59'])
                         .all())

            for val in hpk_today:
                sum = sum + val.value
            try:
                res = round(sum / len(hpk_today), 2)
            except Exception as _ex:
                print(_ex)
                res = 0
            max_value = ParameterFromAnalogSensorForBBO.objects.filter(name='HPK',
                                                                       time__range=[
                                                                           f'{datetime.datetime.today().date()} 00:00:00',
                                                                           f'{datetime.datetime.today().date()} 23:59:59']).aggregate(
                Max('value'))

            avg_HPK_today = res
            avg_HPK_yesterday = None
            max_HPK_yesterday = None
            try:
                avg_HPK_yesterday = ParameterFromAnalogSensorForBBO.objects.filter(name='avg_HPK_yesterday').first()
                max_HPK_yesterday = ParameterFromAnalogSensorForBBO.objects.filter(name='max_HPK_yesterday').first()
            except Exception as _ex:
                print(_ex)
                avg_HPK_yesterday = 0
                max_HPK_yesterday = 0

            return dict(
                bbo1=ParameterFromAnalogSensorForBBOSerializer(qs1, many=True).data,
                bbo2=ParameterFromAnalogSensorForBBOSerializer(qs2, many=True).data,
                bbo3=ParameterFromAnalogSensorForBBOSerializer(qs3, many=True).data,
                bbo4=ParameterFromAnalogSensorForBBOSerializer(qs4, many=True).data,
                common=ParameterFromAnalogSensorForBBOSerializer(qs5, many=True).data,
                air_flow_volume=ManagementVolumeFlowForBBOSerializer(qs6, many=False).data,
                air_concentration1=ManagementConcentrationFlowForBBOSerializer(conc1, many=False).data,
                air_concentration2=ManagementConcentrationFlowForBBOSerializer(conc2, many=False).data,
                air_concentration3=ManagementConcentrationFlowForBBOSerializer(conc3, many=False).data,
                air_concentration4=ManagementConcentrationFlowForBBOSerializer(conc4, many=False).data,
                work_mode=WorkModeSerializer(mode, many=False).data,
                avg_hpk_today=avg_HPK_today,
                max_hpk_today=round(max_value['value__max'], 2),
                avg_hpk_yesterday=HPKSerializer(avg_HPK_yesterday, many=False).data,
                max_hpk_yesterday=HPKSerializer(max_HPK_yesterday, many=False).data,
                bowl1=DistributionBowlSerializer(bowl1, many=False).data,
                bowl2=DistributionBowlSerializer(bowl2, many=False).data,
                bowl3=DistributionBowlSerializer(bowl3, many=False).data,
                bowl4=DistributionBowlSerializer(bowl4, many=False).data,
                current_air_consumption=round(current_air_consumption, 2),
                diffusor=DiffusorSerializer(diffusor, many=False).data,
                silt_pump_state=SiltPumpStationSerializer(silt_state, many=False).data,
                avg_oxy_state=WorkSettingsSingleSerializer(avg_oxy_state, many=False).data,
                oxygen_1_1_state=WorkSettingsSingleSerializer(oxygen_1_1_state, many=False).data,
                oxygen_1_2_state=WorkSettingsSingleSerializer(oxygen_1_2_state, many=False).data,
                oxygen_1_3_state=WorkSettingsSingleSerializer(oxygen_1_3_state, many=False).data,
                oxygen_1_4_state=WorkSettingsSingleSerializer(oxygen_1_4_state, many=False).data,
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
            return dict(data=CommandForBBOSerializer(qs, many=True).data, )


class NotificationConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = NotificationSerializer
    # queryset = Notification.objects.all()
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        loop = asyncio.get_event_loop()
        async_function = sync_to_async(data_func_for_notification)
        ans = loop.create_task(async_function())
        await ans
        answer1 = dict(
            data=ans.result()
        )

        await self.send_json(answer1)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        id = text_data_json["id"]
        is_read = text_data_json["is_read"]
        await change_notify(pk=id, is_read=is_read)


    @model_observer(Notification)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            # qs = Notification.objects.filter(bbo_id=1).order_by('-id')[:10]
            return dict(data=NotificationSerializer(instance, many=False).data, )


class WorkModeConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    serializer_class = WorkModeSerializer
    # queryset = Notification.objects.all()
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()
        loop = asyncio.get_event_loop()
        async_function = sync_to_async(data_func_for_work_mode)
        ans = loop.create_task(async_function())
        await ans
        answer1 = dict(
            data=ans.result()
        )

        await self.send_json(answer1)

    @model_observer(WorkMode)
    async def model_change(self, message, observer=None, **kwargs):
        if message:
            await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        if action.value == 'create':
            # qs = Notification.objects.filter(bbo_id=1).order_by('-id')[:10]
            return dict(data=WorkModeSerializer(instance, many=False).data, )
