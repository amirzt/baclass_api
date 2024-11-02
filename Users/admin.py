from django.contrib import admin

from Users.models import CustomUser, Student, Grade, Wallet, OTP, Banner, HomeMessage, Version

# Register your models here.
admin.site.register(Grade)
admin.site.register(Wallet)
admin.site.register(OTP)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'date_joint')
    list_filter = ('is_student', 'is_advisor', 'is_active', 'is_staff', 'market', 'version')
    search_fields = ('phone__startswith', 'name__startswith')
    fields = ('name', 'phone', 'is_visible', 'is_staff', 'is_active', 'is_student', 'is_advisor', 'market', 'version')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_grade', 'get_gender', 'expire_date')
    list_filter = ('grade', 'gender', 'expire_date')
    search_fields = ('user__phone__startswith', 'user__name__startswith')
    fields = ('user', 'grade', 'gender', 'expire_date')


admin.site.register(Banner)
admin.site.register(HomeMessage)
admin.site.register(Version)
