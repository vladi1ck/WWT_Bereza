import asyncio
import datetime
import itertools
import multiprocessing
import threading
import time

import snap7.client
from asgiref.sync import sync_to_async, async_to_sync
from async_signals import Signal, receiver
from django.db.models import Max

from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib.auth.models import User
from snap7.types import Areas
from snap7.util import get_real, get_int, set_int

from . import logic_for_bbo
# from django.dispatch import receiver

from .logic_for_bbo import ParameterFromAnalogSensorForBBOView
from .models import ManagementConcentrationFlowForBBO, CommandForBBO, BBO, Notification, \
    ParameterFromAnalogSensorForBBO, ManagementRecycleForBBO, ManagementVolumeFlowForBBO, WorkMode, NotificationManager

live_1 = True
live_1_1 = True
live_1_2 = True
live_1_3 = True
live_1_4 = True


# class CommandThread(threading.Thread):
#     def __init__(self, instance, **kwargs):
#         self.instance = instance
#         super(CommandThread, self).__init__(**kwargs)
#
#     def run(self):
#         print(self.instance.name)
#
#         print(f'In work, remaining {self.instance.timeout * 60}sec')
#         oxy1 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=self.instance.bbo_id.id).last()
#         oxy2 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=self.instance.bbo_id.id).last()
#         oxy3 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=self.instance.bbo_id.id).last()
#         oxy4 = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=self.instance.bbo_id.id).last()
#         oxygen_1_1 = [oxy1, oxy2, oxy3]
#         oxygen_1_2 = [oxy1]
#         oxygen_1_3 = [oxy2, oxy3]
#         # accidents_1_1 = [oxy1.is_not_accident, oxy2.is_not_accident, oxy3.is_not_accident]
#         accidents_1_2 = [oxy1.is_not_accident]
#         # accidents_1_3 = [oxy2.is_not_accident, oxy3.is_not_accident]
#         average = 0
#         deviation_rate = 0
#         given_value = 0
#         average_1_1 = 0
#         average_1_2 = 0
#         average_1_3 = 0
#         deviation_rate_1_1 = 0
#         deviation_rate_1_2 = 0
#         deviation_rate_1_3 = 0
#         given_value_1_1 = 0
#         given_value_1_2 = 0
#         given_value_1_3 = 0
#         try:
#             middle_requirement_oxygen_1 = oxy1.bbo_rate * (oxy1.current_value - oxy1.given_value)
#             middle_requirement_oxygen_2 = oxy2.bbo_rate * (oxy2.current_value - oxy2.given_value)
#             middle_requirement_oxygen_3 = oxy3.bbo_rate * (oxy3.current_value - oxy3.given_value)
#             middle_requirement_oxygen_4 = oxy4.bbo_rate * (oxy4.current_value - oxy4.given_value)
#         except Exception as ex:
#             print(ex)
#             middle_requirement_oxygen_1 = 0
#             middle_requirement_oxygen_2 = 0
#             middle_requirement_oxygen_3 = 0
#             middle_requirement_oxygen_4 = 0
#         middle_requirement_oxygen = (middle_requirement_oxygen_1 + middle_requirement_oxygen_2 +
#                                      middle_requirement_oxygen_3 + middle_requirement_oxygen_4)
#         print(middle_requirement_oxygen)
#         # for i in itertools.compress(oxygen_1_1, accidents_1_1):
#         #     average_1_1 = average_1_1 + int(i.current_value)
#         #     deviation_rate_1_1 = deviation_rate_1_1 + int(i.deviation_rate)
#         #     given_value_1_1 = given_value_1_1 + int(i.given_value)
#
#         for i in itertools.compress(oxygen_1_2, accidents_1_2):
#             average_1_2 = average_1_2 + int(i.current_value)
#             deviation_rate_1_2 = deviation_rate_1_2 + int(i.deviation_rate)
#             given_value_1_2 = given_value_1_2 + int(i.given_value)
#
#         # for i in itertools.compress(oxygen_1_3, accidents_1_3):
#         #     average_1_3 = average_1_3 + int(i.current_value)
#         #     deviation_rate_1_3 = deviation_rate_1_3 + int(i.deviation_rate)
#         #     given_value_1_3 = given_value_1_3 + int(i.given_value)
#
#         if self.instance.name == 'oxygen_1_2' or 'oxygen_2_2' or 'oxygen_3_2':
#             average = average_1_2
#             deviation_rate = deviation_rate_1_2
#             given_value = given_value_1_2
#             pass
#
#         else:
#             average = 0
#             deviation_rate = 0
#             given_value = 0
#
#         time.sleep(self.instance.timeout * 60)
#         if average < given_value - deviation_rate:
#             print(f'{self.instance.name} - COMMAND: UP')
#             return 1
#         elif average > given_value + deviation_rate:
#             print(f'{self.instance.name} - COMMAND: DOWN')
#             return -1
#         elif average in range(given_value - deviation_rate, given_value + deviation_rate):
#             print(f'{self.instance.name} - COMMAND: Nothing')
#             return 0
#         else:
#             print(f'{self.instance.name} - COMMAND: Error')
#             return -9999

def calc_recycle(bbo_id):
    water = ParameterFromAnalogSensorForBBO.objects.filter(name='water_consumption_in').first().value
    manager = NotificationManager.objects.filter(bbo_id=5).last()
    # water = 720
    recycle = ManagementRecycleForBBO.objects.filter(bbo_id=bbo_id).last()
    nitrate_percent = 0.0
    anaerobe_percent = 0.0
    percent = 0.0
    freq_pump = 0.0

    status = ''
    if water <= recycle.middle_max_value:
        status = ('СРЕДНИЙ РЕЦИКЛ')
        percent = (recycle.middle_max_percent * water) / recycle.middle_max_value
        anaerobe_percent = (recycle.anaerobic_middle_max_percent * water) / recycle.middle_max_value
        nitrate_percent = (recycle.nitrate_middle_max_percent * water) / recycle.middle_max_value
        freq_pump = (recycle.middle_max_value_pump * water) / recycle.middle_max_value

        if percent < recycle.middle_min_percent:
            percent = recycle.middle_min_percent
        if freq_pump < recycle.middle_min_value_pump:
            freq_pump = recycle.middle_min_value_pump
        if anaerobe_percent < recycle.anaerobic_middle_min_percent:
            anaerobe_percent = recycle.anaerobic_middle_min_percent
        if nitrate_percent < recycle.nitrate_middle_min_percent:
            nitrate_percent = recycle.nitrate_middle_min_percent

    if water > recycle.middle_max_value:
        status = ('МАКСИМАЛЬНЫЙ РЕЦИКЛ')

        percent = (recycle.max_max_percent * water) / recycle.max_value
        anaerobe_percent = (recycle.anaerobic_max_max_percent * water) / recycle.max_value
        nitrate_percent = (recycle.nitrate_max_max_percent * water) / recycle.max_value
        freq_pump = (recycle.max_max_value_pump * water) / recycle.max_value

        if (percent >= manager.recycle_valve or freq_pump >= manager.recycle_pump or
                anaerobe_percent >= manager.recycle_valve or nitrate_percent >= manager.recycle_valve):
            Notification.objects.create(
                bbo_id=BBO.objects.get(id=5),
                status_code=1,
                title=recycle.name,
                message=f'[{status}][BBO{bbo_id}] Контролируйте уровень стоков в ББО'
            )
    percent = round(percent)
    freq_pump = round(freq_pump)
    anaerobe_percent = round(anaerobe_percent)
    nitrate_percent = round(nitrate_percent)


    Notification.objects.create(
        bbo_id=BBO.objects.get(id=5),
        status_code=0,
        title=recycle.name,
        message=f'[{status}][BBO{bbo_id}] Установить {percent}% на задвижках'
    )
    Notification.objects.create(
        bbo_id=BBO.objects.get(id=5),
        status_code=0,
        title=recycle.name,
        message=f'[{status}][BBO{bbo_id}] Установить {freq_pump}Гц на насосах'
    )
    Notification.objects.create(
        bbo_id=BBO.objects.get(id=5),
        status_code=0,
        title=recycle.name,
        message=f'[{status}][BBO{bbo_id}] Установить {anaerobe_percent}% на задвижках (Анаэробная зона)'
    )
    Notification.objects.create(
        bbo_id=BBO.objects.get(id=5),
        status_code=0,
        title=recycle.name,
        message=f'[{status}][BBO{bbo_id}] Установить {nitrate_percent}Гц на задвижках (Нитратная зона)'
    )
    if WorkMode.objects.last().mode == 1:
        CommandForBBO.objects.create(
            bbo_id=BBO.objects.get(id=5),
            name=f'recycle_valve{bbo_id}',
            command=None,
            value=percent
        )
        CommandForBBO.objects.create(
            bbo_id=BBO.objects.get(id=5),
            name=f'recycle_pump{bbo_id}',
            command=None,
            value=freq_pump
        )
        CommandForBBO.objects.create(
            bbo_id=BBO.objects.get(id=5),
            name=f'recycle_valve_anaerobe{bbo_id}',
            command=None,
            value=anaerobe_percent
        )
        CommandForBBO.objects.create(
            bbo_id=BBO.objects.get(id=5),
            name=f'recycle_valve_nitrate{bbo_id}',
            command=None,
            value=nitrate_percent
        )
    return


@receiver(signal=post_save, sender=ManagementVolumeFlowForBBO)
def create_notification_volume(instance, **kwargs):
    global live_1

    th1 = threading.Thread(target=calculate_avg_oxygen, args=(instance,))

    if live_1:
        live_1 = False
        th1.start()
    try:
        if th1.is_alive():
            th1.join()
    except Exception as _ex:
        print(_ex)
    finally:
        live_1 = True


def calculate_avg_oxygen(instance, **kwargs):
    concentration = ManagementConcentrationFlowForBBO.objects.filetr(bbo_id=1).last
    result = -9999

    if instance.avg_oxygen_rate < instance.min_avg_oxygen:
        result = 1
    elif instance.avg_oxygen_rate > instance.max_avg_oxygen:
        result = -1
    elif instance.min_avg_oxygen <= instance.avg_oxygen_rate <= instance.max_avg_oxygen:
        result = 0
    if WorkMode.objects.last().mode == 1:

        CommandForBBO.objects.create(
            bbo_id=instance.bbo_id,
            name=instance.name,
            value=result
        )
    time.sleep(concentration.timeout * 60)


def analysis_valve(instance):
    # print(instance.name)
    #
    # print(f'In work, remaining {instance.timeout * 60}sec')

    if instance.is_not_accident:

        min_val = instance.given_value - instance.deviation_rate
        max_val = instance.given_value + instance.deviation_rate


        if instance.current_value < min_val:
            print(f'{instance.name} - COMMAND: UP')
            result = 1
        elif instance.current_value > max_val:
            print(f'{instance.name} - COMMAND: DOWN')
            result = -1
        elif min_val < instance.current_value < max_val:
            print(f'{instance.name} - COMMAND: Nothing')
            result = 0
        else:
            print(f'{instance.name} - COMMAND: Error')
            result = -9999
        if WorkMode.objects.last().mode == 0:
            if result == 1:
                Notification.objects.create(
                    bbo_id=instance.bbo_id,
                    status_code=0,
                    title=instance.name,
                    message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Увеличьте процент открытия затвора подачи воздуха'
                )
            elif result == -1:
                Notification.objects.create(
                    bbo_id=instance.bbo_id,
                    status_code=0,
                    title=instance.name,
                    message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Уменьшите процент открытия затвора подачи воздуха'
                )
            elif result == 0:
                Notification.objects.create(
                    bbo_id=instance.bbo_id,
                    status_code=0,
                    title=instance.name,
                    message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Не требуется регулировка затвора подачи воздуха'
                )
        if WorkMode.objects.last().mode == 1:
            CommandForBBO.objects.create(
                bbo_id=instance.bbo_id,
                name=instance.name,
                value=result
            )
    time.sleep(instance.timeout * 60)


@receiver(signal=post_save, sender=ManagementConcentrationFlowForBBO)
def handler(sender, instance, **kwargs):
    global live_1_1
    global live_1_2
    global live_1_3
    global live_1_4

    th1 = threading.Thread(target=analysis_valve, args=(instance,))
    th2 = threading.Thread(target=analysis_valve, args=(instance,))
    th3 = threading.Thread(target=analysis_valve, args=(instance,))
    th4 = threading.Thread(target=analysis_valve, args=(instance,))

    if instance.name == 'oxygen_1_1' and live_1_1:
        live_1_1 = False
        th1.start()

    elif instance.name == 'oxygen_1_2' and live_1_2:
        live_1_2 = False
        th2.start()

    elif instance.name == 'oxygen_1_3' and live_1_3:
        live_1_3 = False
        th3.start()

    elif instance.name == 'oxygen_1_4' and live_1_4:
        live_1_4 = False
        th4.start()

    try:
        if th1.is_alive():
            th1.join()
        if th2.is_alive():
            th2.join()
        if th3.is_alive():
            th3.join()
        if th4.is_alive():
            th4.join()

    except Exception as _ex:
        print(_ex)
    finally:
        live_1_1 = True
        live_1_2 = True
        live_1_3 = True
        live_1_4 = True


@receiver(signal=post_save, sender=ParameterFromAnalogSensorForBBO)
def for_HPK(sender, instance, **kwargs):
    if instance.name == 'HPK':
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        y_time_start = f'{yesterday.date()} 00:00:00'
        y_time_end = f'{yesterday.date()} 23:59:59'

        yesterday = yesterday.date()
        last_value = ParameterFromAnalogSensorForBBO.objects.filter(name='HPK').first()
        date = last_value.time.date()

        if date != today.date():
            all_values = ParameterFromAnalogSensorForBBO.objects.filter(name='HPK',
                                                                        time__range=[y_time_start, y_time_end]).all()
            max_value = ParameterFromAnalogSensorForBBO.objects.filter(name='HPK', time__range=[y_time_start,
                                                                                                y_time_end]).aggregate(
                Max('value'))

            length = len(all_values)
            sum = 0
            for val in all_values:
                sum = sum + val.value
            res = round(sum / length, 2)
            print(res)
            ParameterFromAnalogSensorForBBO.objects.create(
                bbo_id=instance.bbo_id,
                name='avg_HPK_yesterday',
                value=res,
                rus_name='Средний ХПК за вчера',
            )
            ParameterFromAnalogSensorForBBO.objects.create(
                bbo_id=instance.bbo_id,
                name='max_HPK_yesterday',
                value=round(max_value['value__max'], 2),
                rus_name='Максимальный ХПК за вчера',
            )


@receiver(signal=post_save, sender=ParameterFromAnalogSensorForBBO)
def create_notification(sender, instance, **kwargs):
    # if WorkMode.objects.last().mode == 0:
    manager = NotificationManager.objects.filter(bbo_id=instance.bbo_id).last()

    if instance.name == 'OVP' and instance.value <= manager.OVP_max:
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Возможно идет сброс сточных вод от промышленных промпредприятий, отобрать анализы '
                    'на входе'
        )

    if instance.name == 'acidity' and (instance.value <= manager.ph_min or instance.value >= manager.ph_max):
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходимо провести обследование на наличие сброса промышленных сточных вод '
                    'при возможности запустить резервный осветлитель-перегниватель'
        )

    if instance.name == 'temperature' and instance.value <= manager.temp_min:
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходимо обратить внимание на интенсивность процесса денитрификации'
        )

    if instance.name == 'silt_level':
        if instance.value > manager.level_sludge:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Обеспечьте удаление избыточного ила'
            )

    if instance.name == 'turbidity':
        if instance.value < manager.avg_sludge_min:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходиомо перераспределить потоки активного ила по биоблокам'
            )
        elif instance.value > manager.avg_sludge_max:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходиомо перераспределить потоки активного ила по биоблокам'
            )
    if instance.name == 'water_consumption_in' and instance.value > manager.water:
        Notification.objects.create(
            bbo_id=BBO.objects.get(id=5),
            status_code=0,
            title='common_notice',
            message=f'[{BBO.objects.get(id=5).rus_name}] Есть возможность гидравлической перегрузки сооружений, при возможности сбросить сточные воды в резервные сооружения'
        )

    if instance.name == 'HPK':

        if instance.value > manager.hpk:
            Notification.objects.create(
                bbo_id=BBO.objects.get(id=5),
                status_code=0,
                title='common_notice',
                message=f'[{BBO.objects.get(id=5).rus_name}]  Необходимо провести обследование на наличие сброса промышленных сточных вод, '
                        f'при возможности запустить резервный осветлитель-перегниватель и/либо увеличить откачку сброженного осадка.'
            )

    if instance.name == 'turbidity' and str(instance.bbo_id) == 'BBO4':
        for i in range(4):
            calc_recycle(i+1)
        turb1 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1, name='turbidity').first()
        turb2 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2, name='turbidity').first()
        turb3 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3, name='turbidity').first()
        turb4 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=4, name='turbidity').first()
        val1 = turb1.value
        val2 = turb2.value
        val3 = turb3.value
        val4 = turb4.value
        sum = (val1 + val2 + val3 + val4) / 4
        if sum < manager.avg_sludge_min:
            Notification.objects.create(
                bbo_id=BBO.objects.get(id=5),
                status_code=0,
                title='common_notice',
                message=f'[{BBO.objects.get(id=5).rus_name}] На данный момент отсутствует необходимость в откачке избыточного аткивного ила'
            )
        elif sum > manager.avg_sludge_max:
            Notification.objects.create(
                bbo_id=BBO.objects.get(id=5),
                status_code=0,
                title='common_notice',
                message=f'[{BBO.objects.get(id=5).rus_name}] Необходима откачка избыточного активного ила'
            )
    # if instance.name == 'water_consumption_in':
    #     calc_recycle()


@receiver(signal=post_save, sender=CommandForBBO)
def create_notification(sender, instance, **kwargs):
    if instance.name == 'oxygen_1_1' or instance.name == 'oxygen_1_2' or instance.name == 'oxygen_1_3' or instance.name == 'oxygen_1_4':
        if instance.command == 1:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Увеличьте процент открытия затвора подачи воздуха'
            )
        elif instance.command == -1:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Уменьшите процент открытия затвора подачи воздуха'
            )
        elif instance.command == 0:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Не требуется регулировка затвора подачи воздуха'
            )

    elif instance.name == 'avg_oxy_rate':
        if instance.command == 1:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Увеличьте производительность воздуходувки'
            )
        elif instance.command == -1:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Уменьшите производительность воздуходувки'
            )
        elif instance.command == 0:
            Notification.objects.create(
                bbo_id=instance.bbo_id,
                status_code=0,
                title=instance.name,
                message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Не требуется регулировка производительности воздуходувки'
            )


@receiver(signal=pre_save, sender=WorkMode)
def create_notification_work(sender, instance, **kwargs):
    mode = {
        0: 'Локальный',
        1: 'Автоматический',
    }
    try:
        connect_to_plc(instance=instance, port=102, type_value='real', type_command=0, db=1201, start=996, byte_index=0)
        connect_to_plc(instance=instance, port=4004, type_value='real', type_command=0, db=1201, start=132,
                       byte_index=0)
        connect_to_plc(instance=instance, port=4002, type_value='real', type_command=0, db=1201, start=36,
                       byte_index=0)
        Notification.objects.create(
            bbo_id=BBO.objects.get(id=5),
            status_code=0,
            title='Режим работы',
            message=f'[{BBO.objects.get(id=5).rus_name}] Изменен режим работы на {mode[instance.mode]}'
        )
    except Exception as _ex:
        print(_ex)
        Notification.objects.create(
            bbo_id=BBO.objects.get(id=5),
            status_code=0,
            title='Режим работы',
            message=f'[{BBO.objects.get(id=5).rus_name}] Ошибка в изменение режима'
        )


def connect_to_plc(instance, port, type_value: str, type_command: int, db, start, byte_index):
    # type_value = 0 - bool, 1 - int, 2 - real
    # type_command = 0 - work_mode, 1 - command(up, down, nothing), 2 - value
    url = "46.216.167.211"
    connect = False
    attempt = 2

    while True:
        try:
            if not connect:
                try:
                    plc1 = snap7.client.Client()
                    plc1.connect(url, 0, 0, port)
                    # print(plc1.get_cpu_state())
                    connect = plc1.get_connected()
                    print('plc connect ', connect)
                except Exception as e:
                    connect = False
                    attempt = attempt - 1
                    time.sleep(3)
                    if attempt == 0:
                        connect = True
                    continue
            # connect_to_plc(_plc=plc)
            if connect:
                type_size = {
                    'bool': 1,
                    'int': 2,
                    'real': 4
                }
                data = bytearray(type_size[type_value])

                if type_command == 0:
                    snap7.util.set_real(data, byte_index, instance.mode)
                # elif type_command == 1:
                #     snap7.util.set_int(data, byte_index, instance.command)
                else:
                    snap7.util.set_real(data, byte_index, instance.value)

                plc1.write_area(Areas.DB, db, start, data)
                print(f'{[instance]} Данные успешно отправлены')
                plc1.destroy()
                break
        except Exception as _ex:
            connect = False
            print(f'{[instance]} {_ex}')
            plc1.destroy()
            continue


@receiver(signal=post_save, sender=CommandForBBO)
def post_command(sender, instance, **kwargs):
    if WorkMode.objects.last().mode == 1:
        name = {
            'avg_oxy_rate': {
                'port': 4002,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 52,
                'byte_index': 0,
                'rus_name': 'Воздуходувка'
            },
            'oxygen_1_1': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 1012,
                'byte_index': 0,
                'rus_name': 'Затвор ББО1'
            },
            'oxygen_1_2': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 1028,
                'byte_index': 0,
                'rus_name': 'Затвор ББО2'
            },
            'oxygen_1_3': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 1044,
                'byte_index': 0,
                'rus_name': 'Затвор ББО3'
            },
            'oxygen_1_4': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 1060,
                'byte_index': 0,
                'rus_name': 'Затвор ББО4'
            },
            'recycle_valve1': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 740,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы1'
            },
            'recycle_pump1': {
                'port': 4004,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 68,
                'byte_index': 0,
                'rus_name': 'Рецикл Насосы1'
            },
            'recycle_valve_anaerobe1': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 756,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы1 (анаэробная зона)'
            },
            'recycle_valve_nitrate1': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 772,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы1 (нитратная зона)'
            },
            'recycle_valve2': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 804,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы2'
            },
            'recycle_pump2': {
                'port': 4004,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 84,
                'byte_index': 0,
                'rus_name': 'Рецикл Насосы2'
            },
            'recycle_valve_anaerobe2': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 820,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы2 (анаэробная зона)'
            },
            'recycle_valve_nitrate2': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 836,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы2 (нитратная зона)'
            },
            'recycle_valve3': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 868,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы3'
            },
            'recycle_pump3': {
                'port': 4004,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 100,
                'byte_index': 0,
                'rus_name': 'Рецикл Насосы3'
            },
            'recycle_valve_anaerobe3': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 884,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы3 (анаэробная зона)'
            },
            'recycle_valve_nitrate3': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 900,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы3 (нитратная зона)'
            },
            'recycle_valve4': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 932,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы4'
            },
            'recycle_pump4': {
                'port': 4004,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 116,
                'byte_index': 0,
                'rus_name': 'Рецикл Насосы4'
            },
            'recycle_valve_anaerobe4': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 948,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы4 (анаэробная зона)'
            },
            'recycle_valve_nitrate4': {
                'port': 102,
                'type_value': 'real',
                'type_command': 2,
                'db': 1201,
                'start': 964,
                'byte_index': 0,
                'rus_name': 'Рецикл Затворы4 (нитратная зона)'
            },
        }
        rus = 'rus_name'
        if instance.name in name:
            try:
                th1 = threading.Thread(target=connect_to_plc, args=(instance,
                                                                    name[instance.name]['port'],
                                                                    name[instance.name]['type_value'],
                                                                    name[instance.name]['type_command'],
                                                                    name[instance.name]['db'],
                                                                    name[instance.name]['start'],
                                                                    name[instance.name]['byte_index']))
                th1.start()

                if th1.is_alive():
                    th1.join()
                # connect_to_plc(instance=instance,
                #                port=name[instance.name]['port'],
                #                type_value=name[instance.name]['type_value'],
                #                type_command=name[instance.name]['type_command'],
                #                db=name[instance.name]['db'],
                #                start=name[instance.name]['start'],
                #                byte_index=name[instance.name]['byte_index'])

            except Exception as _ex:
                Notification.objects.create(
                    bbo_id=BBO.objects.get(id=5),
                    status_code=0,
                    title='Ошибка',
                    message=f'[ОШИБКА] Ошибка при отправке команды {name[instance.name][rus]}'
                )
