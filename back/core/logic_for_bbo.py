import datetime
import pdb

from asgiref.sync import sync_to_async
from async_signals import Signal
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import json
# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .serializers import (labValueSerializer, projValueSerializer, ParameterFromAnalogSensorForBBOSerializer,
                          BBOSerializer, ManagementConcentrationFlowForBBOSerializer, CommandForBBOSerializer,
                          NotificationSerializer, ManagementRecycleForBBOSerializer,
                          ManagementVolumeFlowForBBOSerializer, WorkModeSerializer, NotificationManagerSerializer,
                          DistributionBowlSerializer)
from .models import Parameter, User, LabValue, ProjValue, ParameterFromAnalogSensorForBBO, BBO, \
    ManagementConcentrationFlowForBBO, Notification, ManagementRecycleForBBO, WorkMode, NotificationManager, \
    DistributionBowl


class GetDatesForLabValue(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):

        date = []
        objs = LabValue.objects.all()
        i = 0
        for obj in objs:
            if obj.datetime is not None:
                date.insert(i, obj.datetime.date())
                i = i + 1
        # print(date)
        out = list(dict.fromkeys(date))
        # print(out)
        return JsonResponse(out, status=status.HTTP_200_OK, safe=False)


class GetLabValueFromDates(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        lab = []
        labb = {}
        search_date = request.GET.get('search_date')
        objs = LabValue.objects.filter(datetime__date=search_date)
        i = 0
        for obj in objs:
            lab.insert(i, obj.id)

            labb[obj.id] = obj.modified_time
            i = i + 1
        serializer = self.serializer_class(objs, many=True)
        # print(labb)
        return JsonResponse(labb, status=status.HTTP_200_OK, safe=False)


class GetLabValueFromID(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        lab = []
        lab_id = request.GET.get('id')
        objs = LabValue.objects.filter(id=lab_id)

        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateLabValueByID(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, lab_id):
        # lab_id = request.PUT.get('id')
        try:
            lab_val = LabValue.objects.get(pk=lab_id)

        except labValueSerializer.DoesNotExist:
            return JsonResponse({'message': 'The lab_val does not exist'}, status=status.HTTP_404_NOT_FOUND)
        new_data = JSONParser().parse(request)

        tutorial_serializer = labValueSerializer(lab_val, data=new_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostLabValueView(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    # def get_all_values(self):
    #     serializers = {}
    #     values = {}
    #     i = 1
    #     for i in 4:
    #         try:
    #             value = ProjValue.objects.all().filter(bbo_id=i).last()
    #             values.pop(value, i)
    #         except Exception as _ex:
    #             print(_ex)
    #
    #     for value in values:
    #         j = 0
    #         serializer = self.serializer_class(value, many=False)
    #         serializers.pop(serializer, j)
    #         j = j + 1
    #     response = {
    #         'data_bbo_1': serializers.get(0),
    #         'data_bbo_2': serializers.get(1),
    #         'data_bbo_3': serializers.get(2),
    #         'data_bbo_4': serializers.get(3),
    #     }
    #     return response

    def post(self, request):
        if request.data['datetime']:
            datetime_lab = request.data['datetime']
        else:
            datetime_lab = datetime.datetime.now()
        del request.data['datetime']
        if request.data['modified_by']:
            modified = request.data['modified_by']
        del request.data['modified_by']
        for i in range(len(request.data)):
            # print(request.data[f'bbo{i+1}'])
            request.data[f'bbo{i + 1}']['bbo_id'] = i + 1
            request.data[f'bbo{i + 1}']['datetime'] = datetime_lab
            request.data[f'bbo{i + 1}']['modified_by'] = modified

            serializer = self.serializer_class(data=request.data[f'bbo{i + 1}'])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        arr = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = LabValue.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched lab values',
        }
        if len(arr) != 0:
            for i in range(len(arr)):
                response[f'data_bbo_{i + 1}'] = arr[i]
        else:
            response['message'] = 'No Data'

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class GetLabValueView(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        bbo_id = request.data.get("bbo_id")
        values = LabValue.objects.all().filter(bbo_id=bbo_id).last()
        if values is None:
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Laboratory values is empty',
            }
        else:
            serializer = self.serializer_class(values, many=False)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched laboratory values',
                'data': serializer.data,
                'request': request.data

            }
        return Response(response, status=status.HTTP_200_OK)


class PostProjValueView(GenericAPIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def post(self, request):

        if request.data['datetime']:
            datetime_lab = request.data['datetime']
        else:
            datetime_lab = datetime.datetime.now()
        del request.data['datetime']
        if request.data['modified_by']:
            modified = request.data['modified_by']
        del request.data['modified_by']
        for i in range(len(request.data)):
            # print(request.data[f'bbo{i+1}'])
            request.data[f'bbo{i + 1}']['bbo_id'] = i + 1
            request.data[f'bbo{i + 1}']['datetime'] = datetime_lab
            request.data[f'bbo{i + 1}']['modified_by'] = modified

            serializer = self.serializer_class(data=request.data[f'bbo{i + 1}'])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        arr = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = ProjValue.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched project values',
        }
        if len(arr) != 0:
            for i in range(len(arr)):
                response[f'data_bbo_{i + 1}'] = arr[i]
        else:
            response['message'] = 'No Data'

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class GetProjValueView(GenericAPIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        bbo_id = request.data.get("bbo_id")
        values = ProjValue.objects.all().filter(bbo_id=bbo_id).last()
        if values is None:
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Project values is empty',
            }
        else:
            serializer = self.serializer_class(values, many=False)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched project values',
                'data': serializer.data,
                'request': request.data

            }
        return Response(response, status=status.HTTP_200_OK)


class GetAllBBOProjValueView(GenericAPIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        arr = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = ProjValue.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched project values',
        }
        if len(arr) != 0:
            serializer1 = self.serializer_class(ProjValue.objects.filter(bbo_id=1).last(), many=False)
            response['datetime'] = serializer1.data['datetime']
            for i in range(len(arr)):
                response[f'data_bbo_{i + 1}'] = arr[i]
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)


class GetAllBBOLabValueView(GenericAPIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        arr = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = LabValue.objects.filter(bbo_id=bbo + 1).order_by('datetime').last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched laboratory values',
        }
        temp = {}
        if len(arr) != 0:
            serializer1 = self.serializer_class(LabValue.objects.filter(bbo_id=1).order_by('datetime').last(), many=False)
            response['datetime'] = serializer1.data['datetime']
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def stat_detail(request, ):
    bbo_id = request.GET.getlist('bbo_id')
    name = request.GET.getlist('name')
    first_date = request.GET.get('first_date')
    last_date = request.GET.get('last_date')
    stat = {}
    if len(bbo_id) == 0:
        bbo_id = [5]
    if name and bbo_id is not None:
        for i in range(len(bbo_id)):
            for j in range(len(name)):
                if first_date is None:
                    first_date = '2000-01-01 00:00'
                if last_date is None:
                    last_date = datetime.datetime.now()
                try:
                    stat[f'bbo_{bbo_id[i]}_{name[j]}'] = (
                        ParameterFromAnalogSensorForBBOSerializer(
                            (
                                ParameterFromAnalogSensorForBBO.objects.filter(
                                    bbo_id=int(bbo_id[i]),
                                    name=name[j],
                                    time__range=[first_date, last_date]
                                )
                                .order_by('id')
                            ),
                            many=True).data)
                    if not stat[f'bbo_{bbo_id[i]}_{name[j]}']:
                        del stat[f'bbo_{bbo_id[i]}_{name[j]}']
                except ParameterFromAnalogSensorForBBO.DoesNotExist:
                    return JsonResponse({'message': 'Data does not exist'}, status=status.HTTP_404_NOT_FOUND)
        stat_serializer = []
        if request.method == 'GET':
            if stat == {}:
                return JsonResponse({'message': 'Data does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # for i in range(len(stat)):
                #     stat_serializer.append(ParameterFromAnalogSensorForBBOSerializer(stat[i], many=True).data)
                return JsonResponse({'data': stat})
    else:
        return JsonResponse({'msg': 'Error, check data'})


class ParameterFromAnalogSensorForBBOView(GenericAPIView):
    serializer_class = ParameterFromAnalogSensorForBBOSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = JSONParser().parse(request)
        for i in range(len(data)):
            # print(request.data[f'bbo{i+1}'])

            serializer = self.serializer_class(data=data[i])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved parameter values',
        }

        return Response(response, status=status_code)

    def popost(self, request):
        data = JSONParser().parse(request)
        serializer = ParameterFromAnalogSensorForBBOSerializer(data=data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved parameter values',
        }
        return Response(response, status=status_code)


class AllParameterFromAnalogSensorForBBO1View(ListCreateAPIView):
    serializer_class = ParameterFromAnalogSensorForBBOSerializer
    queryset = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=1)


class AirManagerView(GenericAPIView):
    serializer_class = ManagementConcentrationFlowForBBOSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        values1 = ManagementConcentrationFlowForBBO.objects.all().filter(bbo_id=1).last()
        serializer1 = self.serializer_class(values1, many=False)
        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched values',
            'data_bbo_1': serializer1.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):

        data = JSONParser().parse(request)
        nam_6 = data['name'][:6]
        data['current_value'] = ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=data['bbo_id'],
                                                                               name=nam_6).first().value
        if ParameterFromAnalogSensorForBBO.objects.filter(bbo_id=data['bbo_id'], name=nam_6).first().is_accident:
            data['is_not_accident'] = False
        else:
            data['is_not_accident'] = True
        serializer = ManagementConcentrationFlowForBBOSerializer(data=data)

        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()
            my_signal = Signal(debug=True)

        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved values',
        }
        return Response(response, status=status_code)


class CommandForBBOView(GenericAPIView):
    serializer_class = CommandForBBOSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = JSONParser().parse(request)
        serializer = CommandForBBOSerializer(data=data)

        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved values',
        }
        return Response(response, status=status_code)


def calculate_avg_oxygen():
    oxygen = []

    for i in range(4):
        oxy = ManagementConcentrationFlowForBBO.objects.filter(bbo_id=i + 1).last()
        iteration = oxy.bbo_rate * (oxy.current_value - oxy.given_value)
        oxygen.insert(i, iteration)
        print(iteration)

    avg_oxy_rate = sum(oxygen)
    print(f'Средний кислород - {avg_oxy_rate}')
    return avg_oxy_rate


class ManagementVolumeFlowForBBOView(GenericAPIView):
    serializer_class = ManagementVolumeFlowForBBOSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = JSONParser().parse(request)

        avg_oxy = calculate_avg_oxygen()
        data['avg_oxygen_rate'] = avg_oxy

        serializer = ManagementVolumeFlowForBBOSerializer(data=data)

        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved values',
        }

        return Response(response, status=status_code)


class ManagementRecycleForBBOView(GenericAPIView):
    serializer_class = ManagementRecycleForBBOSerializer
    permission_classes = (AllowAny,)

    def get(self, request):

        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = ManagementRecycleForBBO.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                new_data = data.copy()
                for i in new_data:
                    if new_data[f'{i}'] is None:
                        del data[i]
                # print(data)
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched notification border values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        for i in range(len(data)):
            # print(request.data[f'bbo{i + 1}'])

            serializer = self.serializer_class(data=data[f'bbo{i + 1}'])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = ManagementRecycleForBBO.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                new_data = data.copy()
                for i in new_data:
                    if new_data[f'{i}'] is None:
                        del data[i]
                # print(data)
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully saved notification border values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)


class WorkModeView(GenericAPIView):
    serializer_class = WorkModeSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        # print(request.data)
        # data = JSONParser().parse(request)
        serializer = WorkModeSerializer(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        current_mode = WorkMode.objects.last()
        response = {
            'success': True,
            'status_code': status_code,
            'mode': current_mode.mode,
            'message': 'Successfully saved values',
        }

        return Response(response, status=status_code)


class NotificationManagerView(GenericAPIView):
    serializer_class = NotificationManagerSerializer
    permission_classes = (AllowAny,)

    def get(self, request):

        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = NotificationManager.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                new_data = data.copy()
                for i in new_data:
                    if new_data[f'{i}'] is None:
                        del data[i]
                # print(data)
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched notification border values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        print(request)
        data = JSONParser().parse(request)

        for i in range(len(data)):
            print(request.data[f'bbo{i + 1}'])

            serializer = self.serializer_class(data=data[f'bbo_{i + 1}'])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = NotificationManager.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data
                new_data = data.copy()
                for i in new_data:
                    if new_data[f'{i}'] is None:
                        del data[i]
                # print(data)
                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully saved notification border values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)


class DistributionBowlView(GenericAPIView):
    serializer_class = DistributionBowlSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = DistributionBowl.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data

                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully saved distribution bowl values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        data = JSONParser().parse(request)
        # print(data)

        for i in range(len(data)):
            # print(data[f'bbo{i + 1}'])

            serializer = self.serializer_class(data=data[f'bbo{i + 1}'])
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                status_code = status.HTTP_200_OK
                serializer.save()

        arr = []
        data = []
        bbos = BBO.objects.all()
        for bbo in range(len(bbos)):
            val = DistributionBowl.objects.filter(bbo_id=bbo + 1).last()
            if val is not None:
                data = self.serializer_class(val, many=False).data

                arr.insert(bbo, data)

        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully saved distribution bowl values',
        }
        temp = {}
        if len(arr) != 0:
            for i in range(len(arr)):
                temp[f'bbo_{i + 1}'] = arr[i]
            response['data'] = temp
        else:
            response['message'] = 'No Data'

        return Response(response, status=status.HTTP_200_OK)
