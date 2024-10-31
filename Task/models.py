from django.db import models

from Users.models import Grade, CustomUser, Student

# Create your models here.
LESSON_TYPE = [
    ('عمومی', 1),
    ('اختصاصی', 2)
]


class Lesson(models.Model):
    title = models.CharField(max_length=30, null=False, blank=False)
    types = models.CharField(choices=LESSON_TYPE, max_length=7)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='Lessons/', null=True, blank=True)

    def __str__(self):
        return self.title + " " + self.grade.title


class Category(models.Model):
    title = models.CharField(max_length=30, null=False, blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    description = models.TextField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)

    time = models.IntegerField(null=True, blank=True)
    question = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.user.phone
