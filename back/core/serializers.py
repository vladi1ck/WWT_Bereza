from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Parameter, User, LabValue, ProjValue
from rest_framework.validators import UniqueTogetherValidator
from django.utils import dateformat
from django.conf import settings
from datetime import datetime

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'password','first_name', 'last_name')
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }
#
#     def create(self, validated_data):
#         password = validated_data.pop('password', None)
#         instance = self.Meta.model(**validated_data)
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         return instance

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = '__all__'

class ParameterSerializerForSave(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name', 'value')


class AuthUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'role'
        )

    def create(self, validated_data):
        if validated_data=="1":
            auth_user = User.objects.create_superuser(**validated_data)
        else:
            auth_user = User.objects.create_user(**validated_data)
        return auth_user


class AuthUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def create(self, validated_date):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Пользователя не существует")

        try:
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            refresh['username'] = user.username

            access = AccessToken.for_user(user)
            access['role'] = user.role
            access['username'] = user.username

            refresh_token = str(refresh)
            access_token = str(access)

            update_last_login(None, user)

            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'username': user.username,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'role': user.role,


            }
            return validation
        except Exception:
            raise serializers.ValidationError("Неверные данные для входа")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'role',
            'id',
        )


class labValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabValue
        fields = '__all__'


class projValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjValue
        fields = '__all__'