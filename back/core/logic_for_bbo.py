from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .serializers import (labValueSerializer, projValueSerializer, ParameterFromAnalogSensorForBBOSerializer)
from .models import Parameter, User, LabValue, ProjValue, ParameterFromAnalogSensorForBBO


class PostLabValueView(APIView):
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
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        values1 = LabValue.objects.all().filter(bbo_id=1).last()
        values2 = LabValue.objects.all().filter(bbo_id=2).last()
        values3 = LabValue.objects.all().filter(bbo_id=3).last()
        values4 = LabValue.objects.all().filter(bbo_id=4).last()
        # if values1 or values2 or values3 or values4 is None:
        #     response = {
        #         'success': True,
        #         'status_code': status.HTTP_200_OK,
        #         'message': 'Project values is empty',
        #     }
        # else:
        serializer1 = self.serializer_class(values1, many=False)
        serializer2 = self.serializer_class(values2, many=False)
        serializer3 = self.serializer_class(values3, many=False)
        serializer4 = self.serializer_class(values4, many=False)
        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully saved laboratory values',
            'data_bbo_1': serializer1.data,
            'data_bbo_2': serializer2.data,
            'data_bbo_3': serializer3.data,
            'data_bbo_4': serializer4.data,
        }
        return Response(response, status=status_code)


class GetLabValueView(APIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        bbo_id = request.data.get("bbo_id")
        values = ProjValue.objects.all().filter(bbo_id=bbo_id).last()
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


class PostProjValueView(APIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

        values1 = ProjValue.objects.all().filter(bbo_id=1).last()
        values2 = ProjValue.objects.all().filter(bbo_id=2).last()
        values3 = ProjValue.objects.all().filter(bbo_id=3).last()
        values4 = ProjValue.objects.all().filter(bbo_id=4).last()
        # if values1 or values2 or values3 or values4 is None:
        #     response = {
        #         'success': True,
        #         'status_code': status.HTTP_200_OK,
        #         'message': 'Project values is empty',
        #     }
        # else:
        serializer1 = self.serializer_class(values1, many=False)
        serializer2 = self.serializer_class(values2, many=False)
        serializer3 = self.serializer_class(values3, many=False)
        serializer4 = self.serializer_class(values4, many=False)
        response = {
            'success': True,
            'status_code': status_code,
            'message': 'Successfully fetched project values',
            'data_bbo_1': serializer1.data,
            'data_bbo_2': serializer2.data,
            'data_bbo_3': serializer3.data,
            'data_bbo_4': serializer4.data,

        }
        return Response(response, status=status_code)


class GetProjValueView(APIView):
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


class GetAllBBOProjValueView(APIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        values1 = ProjValue.objects.all().filter(bbo_id=1).last()
        values2 = ProjValue.objects.all().filter(bbo_id=2).last()
        values3 = ProjValue.objects.all().filter(bbo_id=3).last()
        values4 = ProjValue.objects.all().filter(bbo_id=4).last()
        # if values1 or values2 or values3 or values4 is None:
        #     response = {
        #         'success': True,
        #         'status_code': status.HTTP_200_OK,
        #         'message': 'Project values is empty',
        #     }
        # else:
        serializer1 = self.serializer_class(values1, many=False)
        serializer2 = self.serializer_class(values2, many=False)
        serializer3 = self.serializer_class(values3, many=False)
        serializer4 = self.serializer_class(values4, many=False)
        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched project values',
            'data_bbo_1': serializer1.data,
            'data_bbo_2': serializer2.data,
            'data_bbo_3': serializer3.data,
            'data_bbo_4': serializer4.data,

        }
        return Response(response, status=status.HTTP_200_OK)


class GetAllBBOLabValueView(APIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        values1 = LabValue.objects.all().filter(bbo_id=1).last()
        values2 = LabValue.objects.all().filter(bbo_id=2).last()
        values3 = LabValue.objects.all().filter(bbo_id=3).last()
        values4 = LabValue.objects.all().filter(bbo_id=4).last()
        # if values1 or values2 or values3 or values4 is None:
        #     response = {
        #         'success': True,
        #         'status_code': status.HTTP_200_OK,
        #         'message': 'Project values is empty',
        #     }
        # else:
        serializer1 = self.serializer_class(values1, many=False)
        serializer2 = self.serializer_class(values2, many=False)
        serializer3 = self.serializer_class(values3, many=False)
        serializer4 = self.serializer_class(values4, many=False)
        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched laboratory values',
            'data_bbo_1': serializer1.data,
            'data_bbo_2': serializer2.data,
            'data_bbo_3': serializer3.data,
            'data_bbo_4': serializer4.data,

        }
        return Response(response, status=status.HTTP_200_OK)


class ParameterFromAnalogSensorForBBOView(APIView):
    serializer_class = ParameterFromAnalogSensorForBBOSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
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


class AllParameterFromAnalogSensorForBBO1View(APIView):
    serializer_class = ParameterFromAnalogSensorForBBOSerializer

    def get_bbo1_data(self):
        data = ParameterFromAnalogSensorForBBO.objects().filter(bbo_id=1).order_by('time')[:5]
        serializer_data = self.serializer_class(data, many=True)
        response = {
            serializer_data
        }
        return response
