from datetime import datetime, timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from Users.managers import CustomUserManager
from django.utils import timezone
import datetime

MARKET = [
    ('بازار', 1),
    ('مایکت', 2),
    ('نامشخص', 3)
]

GENDER = [
    ('پسر', 1),
    ('دختر', 2),
    ('نامشخص', 3)
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50, null=True, blank=False)
    user_name = models.CharField(max_length=50, null=True, blank=False, unique=True)
    phone = models.CharField(max_length=11, null=False, blank=False, unique=True)
    email = models.EmailField(null=True, blank=False, unique=True)

    is_visible = models.BooleanField(default=True)
    date_joint = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    is_student = models.BooleanField(default=False)
    is_advisor = models.BooleanField(default=False)

    market = models.CharField(default=3, choices=MARKET, max_length=6)
    version = models.CharField(default='1.1.0', max_length=20)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class Grade(models.Model):
    title = models.CharField(max_length=30, blank=False)

    def __str__(self):
        return self.title


def in_seven_days():
    return datetime.now() + timedelta(days=-1)


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, default=3, max_length=6)
    expire_date = models.DateTimeField(default=in_seven_days)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone

    def get_grade(self):
        return "%s" % self.grade

    def get_gender(self):
        return "%s" % self.gender


def get_random_code():
    from random import randint
    return str(randint(1000, 9999))


class OTP(models.Model):
    code = models.CharField(max_length=4, default=get_random_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.created_at + datetime.timedelta(minutes=2)


class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coin = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone