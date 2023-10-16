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

from .serializers import (labValueSerializer, projValueSerializer)
from .models import Parameter, User, LabValue, ProjValue


class PostLabValueView(APIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

            response = {
                'success': True,
                'statusCode': status_code,
            }

            return Response(response, status=status_code)


class GetLabValueView(APIView):
    serializer_class = labValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        values = LabValue.objects.all().last()
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
                'data': serializer.data

            }
        return Response(response, status=status.HTTP_200_OK)


class PostProjValueView(APIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()

            response = {
                'success': True,
                'statusCode': status_code,
            }

            return Response(response, status=status_code)


class GetProjValueView(APIView):
    serializer_class = projValueSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        values = ProjValue.objects.all().last()
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
                'data': serializer.data

            }
        return Response(response, status=status.HTTP_200_OK)