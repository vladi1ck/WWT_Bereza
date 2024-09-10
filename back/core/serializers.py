from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.relations import StringRelatedField, PrimaryKeyRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Parameter, User, LabValue, ProjValue, ParameterFromAnalogSensorForBBO, BBO, \
    ManagementConcentrationFlowForBBO, CommandForBBO, Notification, ManagementRecycleForBBO, ManagementVolumeFlowForBBO, \
    WorkMode, NotificationManager, DistributionBowl, Diffusor, WorkSettingsGroup, WorkSettingsSingle, SiltPumpStation
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
        if validated_data == "1":
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
    id = serializers.CharField(read_only=True)

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
                'id': user.id,

            }
            return validation
        except Exception:
            raise serializers.ValidationError("Неверные данные для входа")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'role',
            'id',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'role',)


class UserPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)


class labValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabValue
        fields = '__all__'


class projValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjValue
        fields = '__all__'


class ParameterFromAnalogSensorForBBOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterFromAnalogSensorForBBO
        exclude = ('id',)


class HPKSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterFromAnalogSensorForBBO
        fields = ('name', 'value', 'time')


class BBOSerializer(serializers.ModelSerializer):
    val = ParameterFromAnalogSensorForBBOSerializer(many=True, read_only=True)

    class Meta:
        model = BBO
        exclude = ('modified_by',)


class ManagementConcentrationFlowForBBOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementConcentrationFlowForBBO
        exclude = ('id',)


class CommandForBBOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandForBBO
        exclude = ('id',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ('id',)


class ManagementRecycleForBBOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementRecycleForBBO
        fields = '__all__'


class ManagementVolumeFlowForBBOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementVolumeFlowForBBO
        fields = '__all__'


class WorkModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkMode
        fields = '__all__'


class NotificationManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationManager
        fields = '__all__'


class DistributionBowlSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionBowl
        fields = '__all__'


class DiffusorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diffusor
        fields = '__all__'


class WorkSettingsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSettingsGroup
        fields = '__all__'


class WorkSettingsSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSettingsSingle
        fields = '__all__'


class SiltPumpStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiltPumpStation
        fields = '__all__'
