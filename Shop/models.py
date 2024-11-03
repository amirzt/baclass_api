from django.db import models

from Users.models import CustomUser


class ZarinpalCode(models.Model):
    code = models.CharField(max_length=255, null=False, blank=False)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Package(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    coin = models.FloatField(default=0)
    discount = models.IntegerField(default=0)
    sku = models.CharField(max_length=200)
    is_available = models.BooleanField(default=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class GatewayChoices(models.TextChoices):
        ZARINPAL = 'zarinpal'
        GOOGLEPLAY = 'googleplay'
        APPSTORE = 'appstore'
        BAZAR = 'bazar'
        MYKET = 'myket'

    class StateChoices(models.TextChoices):
        PENDING = 'pending'
        SUCCESS = 'success'
        FAILED = 'failed'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, null=True)
    price = models.FloatField(null=False, blank=False)
    discount = models.FloatField(null=True, blank=True)
    gateway = models.CharField(max_length=255, choices=GatewayChoices.choices)
    gateway_code = models.CharField(max_length=255, null=True)
    tracking_code = models.CharField(max_length=255, null=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, choices=StateChoices.choices, default=StateChoices.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone + ' - ' + self.package.name
