import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .manager import CustomUserManager


# Create your models here.

class User(AbstractBaseUser):

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
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
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


class Parameter(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)