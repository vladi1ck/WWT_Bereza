import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from .manager import CustomUserManager


# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 1
    ENGINEER = 2
    OPERATOR = 3
    TECHNICIAN = 4

    ROLE_CHOICES = (
        (ADMIN, 'Админ'),
        (ENGINEER, 'Технолог'),
        (OPERATOR, 'Оператор'),
        (TECHNICIAN, 'Лаборант')
    )

    id = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='ID', primary_key=True)
    username = models.CharField(max_length=30, blank=False, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    # password = models.CharField(max_length=255)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        """
        String for representing the MyModelName object (in Admin site etc.)
        """
        return self.username


class Parameter(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)


class BBO(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    modified_by = models.ForeignKey(to=User, on_delete=models.CASCADE, editable=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.name}'


class LabValue(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='lab_id', on_delete=models.CASCADE, editable=True, default="")
    doseFromWeight = models.FloatField()
    doseFromVolume = models.FloatField()
    ashPercent = models.FloatField()
    concentrationExcessActive = models.FloatField()
    suspendSubstSourceWater = models.FloatField()
    suspendSubstAfterSettling = models.FloatField()
    suspendSubstInPurified = models.FloatField()
    bpkInputOS = models.FloatField()
    xpkInputAero = models.FloatField()
    bpkInputAero = models.FloatField()
    bpkOutputAero = models.FloatField()
    nitrogenAmmoniumInputAero = models.FloatField()
    nitrogenAmmoniumOutputAero = models.FloatField()
    nitrogenNitriteInputAero = models.FloatField()
    nitrogenNitriteOutputAero = models.FloatField()
    nitrogenNitrateInputAero = models.FloatField()
    nitrogenNitrateOutputAero = models.FloatField()
    totalNitrogenInputBO = models.FloatField()
    organicNitrogenOutputAero = models.FloatField()
    totalPhosphorusOutput = models.FloatField()
    totalPhosphorusOutputBO = models.FloatField()
    modified_time = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(to=User, on_delete=models.CASCADE, editable=True)

    def __str__(self) -> str:
        return f'{self.bbo_id}'


class ProjValue(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='project_id', on_delete=models.CASCADE, editable=True, default="")
    tankHeight = models.FloatField()
    tankSchema = models.CharField(max_length=255)
    tankArea = models.FloatField()
    tankVolume = models.FloatField()
    nitrificationVolume = models.FloatField()
    denitrificationVolume = models.FloatField()
    anaerobicsVolume = models.FloatField()
    modified_time = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(to=User, on_delete=models.CASCADE, editable=True)

    def __str__(self) -> str:
        return f'{self.bbo_id}'


class ParameterFromAnalogSensorForBBO(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='parameter_analog_id', on_delete=models.CASCADE, editable=True,
                               default="")
    name = models.CharField(max_length=255, null=False)
    value = models.FloatField()
    is_main = models.BooleanField(default=False)
    is_masked = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    is_accident = models.BooleanField(default=False)  # Авария - показания датчика неккоректны
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.name}'


# Положение затвора - текущая концентрация кислорода
class ManagementConcentrationFlowForBBO(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='air_concentration_management_id', on_delete=models.CASCADE,
                               editable=True,
                               default="")
    name = models.CharField(max_length=255, null=False)
    current_value = models.FloatField()
    given_value = models.FloatField()
    deviation_rate = models.FloatField()
    bbo_rate = models.FloatField()
    timeout = models.FloatField()

    def __str__(self) -> str:
        return f'{self.name}'


# Требуемый объем подачи воздуха воздуходувкой
class ManagementVolumeFlowForBBO(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='air_volume_management_id', on_delete=models.CASCADE, editable=True,
                               default="")
    avg_oxygen_rate = models.FloatField()  # записывать значения во вьюхе (где его брать???) при получение создавать?
    min_avg_oxygen = models.FloatField()
    max_avg_oxygen = models.FloatField()
    given_workflow_for_blower = models.FloatField()
    step_for_setup_blower = models.FloatField()
    freq_for_setup_blower = models.FloatField()
    air_consumption = models.FloatField()
    current_pressure = models.FloatField()
    timeout = models.FloatField()


    def __str__(self) -> str:
        return f'{self.name}'


class CommandForBBO(models.Model):
    bbo_id = models.ForeignKey(to=BBO, related_name='air_command_id', on_delete=models.CASCADE, editable=True,
                               default="")
    name = models.CharField(max_length=255, null=False) # Название нужной комманды
    command = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
