import django.core.exceptions
import rest_framework.permissions
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .serializers import (ParameterSerializer, ParameterSerializerForSave,
                          AuthUserLoginSerializer, AuthUserRegistrationSerializer, UserListSerializer, UserSerializer,
                          UserPassSerializer)
from .models import Parameter, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ParameterView(viewsets.ModelViewSet):
    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()


@api_view(['POST'])
def upldParameter(request):
    data = JSONParser().parse(request)
    serializer = ParameterSerializerForSave(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


class AuthUserLoginView(GenericAPIView):
    serializer_class = AuthUserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User logged in successfully',
                'access': serializer.data['access'],
                'refresh': serializer.data['refresh'],
                'authenticatedUser': {
                    'username': serializer.data['username'],
                    'role': serializer.data['role'],
                    'id': serializer.data['id'],
                }
            }

            return Response(response, status=status_code)


class AuthUserRegistrationView(GenericAPIView):
    serializer_class = AuthUserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()
            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User successfully registered!',
                'user': serializer.data["username"]
            }

            return Response(response, status=status_code)


class LogoutView(GenericAPIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response("Logout Successful", status=status.HTTP_200_OK)
        except TokenError:
            raise AuthenticationFailed("Invalid Token")


class UserListView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        user = request.user
        if user.role != 1:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)


class UserChangeView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            print(user)
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        new_data = JSONParser().parse(request)
        print(new_data)
        user_serializer = UserSerializer(user, data=new_data)
        if user_serializer.is_valid():
            user_serializer.save()
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user.delete()
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception:
            return JsonResponse(UserSerializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)


class UserDeletePasswordView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user.password = 0
            user.save()
            return JsonResponse({'message': 'Successfully deleted password'}, status=status.HTTP_200_OK)
        except Exception as _ex:
            return JsonResponse({'message': f'{_ex}'}, status=status.HTTP_400_BAD_REQUEST)


class UserSetNewPassword(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        new_data = JSONParser().parse(request)
        print(new_data)
        try:
            user.set_password(new_data['password'])
            user.save()
            return JsonResponse({'message': 'Successfully changed password'}, status=status.HTTP_200_OK)
        except django.core.exceptions.FieldError:
            return JsonResponse({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
