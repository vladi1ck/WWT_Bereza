import asyncio
import itertools
import multiprocessing
import threading
import time

from asgiref.sync import sync_to_async, async_to_sync
from async_signals import Signal, receiver

from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib.auth.models import User

from . import logic_for_bbo
# from django.dispatch import receiver

from .logic_for_bbo import ParameterFromAnalogSensorForBBOView
from .models import ManagementConcentrationFlowForBBO, CommandForBBO, BBO, Notification, \
    ParameterFromAnalogSensorForBBO

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


def calculate_avg_oxygen():
    oxygen = []

    for i in range(4):
        oxy = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=i+1).last()
        iteration = oxy.bbo_rate * (oxy.current_value - oxy.given_value)
        oxygen.insert(i, iteration)
        print(iteration)

    avg_oxy_rate = sum(oxygen)
    print(f'Средний кислород - {avg_oxy_rate}')


def analysis_valve(instance):
    print(instance.name)

    print(f'In work, remaining {instance.timeout * 60}sec')

    if instance.is_not_accident:

        min_val = instance.given_value - instance.deviation_rate
        max_val = instance.given_value + instance.deviation_rate

        time.sleep(instance.timeout * 60)
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

        CommandForBBO.objects.create(
            bbo_id=instance.bbo_id,
            name=instance.name,
            command=result
        )


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
def create_notification(sender, instance, **kwargs):
    if instance.name == 'OVP' and instance.value <= -200.0:
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Возможно идет сброс сточных вод от промышленных промпредприятий, отобрать анализы '
                    'на входе'
        )

    if instance.name == 'acidity' and (instance.value <= 6.5 or instance.value >= 8.5):
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходимо провести обследование на наличие сброса промышленных сточных вод, '
                    'при возможности запустить резервный осветлитель-перегниватель'
        )

    if instance.name == 'temperature' and instance.value <= 15.0:
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходимо обратить внимание на интенсивность процесса денитрификации'
        )

    if instance.name == 'turbidity' and instance.value <= 2.0:
        Notification.objects.create(
            bbo_id=instance.bbo_id,
            status_code=0,
            title=instance.name,
            message=f'[{BBO.objects.get(name=instance.bbo_id).rus_name}] Необходиомо перераспределить потоки активного ила по биоблокам'
        )
    if instance.name == 'turbidity' and instance.bbo_id == 'BBO4':
        turb1 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1, name='turbidity').last()
        turb2 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=2, name='turbidity').last()
        turb3 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=3, name='turbidity').last()
        turb4 = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=4, name='turbidity').last()
        val1 = turb1.value
        val2 = turb2.value
        val3 = turb3.value
        val4 = turb4.value
        sum = (val1 + val2 + val3 + val4) / 4
        if sum < 2:
            Notification.objects.create(
                bbo_id=BBO.objects.get(id=5),
                status_code=0,
                title='common_notice',
                message=f'[{BBO.objects.get(id=5)}] На данный момент отсутствует необходимость в откачке избыточного аткивного ила'
            )


@receiver(signal=post_save, sender=CommandForBBO)
def create_notification(sender, instance, **kwargs):
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
    if instance.name == 'oxygen_1_4':
        calculate_avg_oxygen()
