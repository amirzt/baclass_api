from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from Task.models import Task
from Task.serializers import AddTaskSerializer, TaskSerializer
from Users.models import Student
from utils.ownership import IsOwner


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['due_date', 'is_done']

    def get_queryset(self):
        student = self.get_student()
        tasks = Task.objects.select_related('student__user').filter(student=student)

        return tasks.order_by('is_done')

    def get_serializer_class(self):
        # Use different serializers for create and other actions
        if self.action == 'create':
            return AddTaskSerializer
        return TaskSerializer

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        serializer = self.get_serializer(data=request.data, context={'student': student})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Use partial updates by default for flexibility
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        student = self.get_student()
        if instance.student != student:
            return Response({"detail": "Not authorized to delete this task."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({"detail": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def get_student(self):
        return get_object_or_404(Student, user=self.request.user)
