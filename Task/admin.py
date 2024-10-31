from django.contrib import admin

from Task.models import Task, Category, Lesson

# Register your models here.
admin.site.register(Task)

admin.site.register(Category)

admin.site.register(Lesson)