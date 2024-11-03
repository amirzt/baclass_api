from django.contrib import admin

from Shop.models import ZarinpalCode, Package, Transaction


# Register your models here.

@admin.register(ZarinpalCode)
class ZarinpalCodeAdmin(admin.ModelAdmin):
    list_display = ('code',)
    fields = ('code', 'is_available',)


@admin.register(Package)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name__startswith',)
    fields = ('name', 'description', 'price', 'is_available', 'discount', 'sku', 'image', 'coin')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'state', 'tracking_code')
    # search_fields = ('title__startswith',)
    fields = (
        'user', 'description', 'price', 'discount', 'gateway', 'gateway_code', 'tracking_code', 'package', 'state',)
