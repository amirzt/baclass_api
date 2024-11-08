from django.db.models import Count
from django.db.models.functions import TruncDate, datetime, ExtractWeekDay
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Task.models import Task
from Task.serializers import AddTaskSerializer, TaskSerializer
from Users.models import Student
from utils.calculate_scores import calculate_score
from utils.date_functions import get_start_of_week
from utils.ownership import IsOwner

import datetime


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
        if self.action == 'create' or self.action == 'update':
            return AddTaskSerializer
        return TaskSerializer

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        serializer = self.get_serializer(data=request.data, context={'student': student})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        calculate_score(user=student.user, category='add_task', due_date=task.due_date)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Use partial updates by default for flexibility
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial,
                                         context={'student': self.get_student()})
        serializer.is_valid(raise_exception=True)
        task = serializer.update(instance, serializer.data)
        if task.is_done:
            calculate_score(user=task.student.user, category='complete_task', due_date=task.due_date)
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

    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        if 'due_date' not in request.query_params:
            return Response({"message": "due date is required"}, status=status.HTTP_400_BAD_REQUEST)
        tasks = tasks.filter(due_date=request.query_params['due_date'])
        return Response(self.get_serializer(tasks, many=True).data)


class ChartViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_student(self):
        return get_object_or_404(Student, user=self.request.user)

    @action(detail=False, methods=['get', ], permission_classes=[IsAuthenticated])
    def chart(self, request):
        student = self.get_student()
        chart_type = request.query_params.get('type')
        period = request.query_params.get('period')

        if not chart_type:
            return Response({'error': 'type is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not period:
            return Response({'error': 'period is required'}, status=status.HTTP_400_BAD_REQUEST)

        if period == 'week':
            start_date = get_start_of_week(datetime.datetime.today())
            end_date = start_date + datetime.timedelta(days=7)
        elif period == 'month':
            end_date = datetime.datetime.today()
            start_date = end_date - datetime.timedelta(days=30)
        elif period == 'year':
            end_date = datetime.datetime.today()
            start_date = end_date - datetime.timedelta(days=365)
        else:
            return Response({'error': 'period is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        if chart_type == 'finished':
            return Response({'finished': self.get_queryset().filter(is_done=True,
                                                                    due_date__range=(start_date, end_date)).count(),
                             'not_finished': self.get_queryset().filter(is_done=False,
                                                                        due_date__range=(start_date, end_date)).count(),
                             'total': self.get_queryset().filter(due_date__range=(start_date, end_date)).count(),
                             }, status=status.HTTP_200_OK)
        elif chart_type == 'due_date':
            done_tasks = (
                Task.objects.filter(
                    student=student,
                    is_done=True,
                    due_date__range=(start_date, end_date)
                )
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            all_tasks = (
                Task.objects.filter(
                    student=student,
                    due_date__range=(start_date, end_date)
                )
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            done_result = {str(entry['date']): entry['count'] for entry in done_tasks}
            all_result = {str(entry['date']): entry['count'] for entry in all_tasks}
            return Response({'done': done_result, 'all': all_result}, status=status.HTTP_200_OK)
        elif chart_type == 'lesson':

            lesson_tasks = self.get_queryset().filter(student=student,
                                                      lesson__isnull=False,
                                                      due_date__range=(start_date, end_date))

            done_tasks_by_lesson = (
                lesson_tasks.filter(
                    is_done=True
                )
                .values('lesson__id', 'lesson__title')
                .annotate(count=Count('id'))
            )

            done_result = {entry['lesson__title']: entry['count'] for entry in done_tasks_by_lesson}

            all_tasks_by_lesson = (
                lesson_tasks
                .values('lesson__id', 'lesson__title')
                .annotate(count=Count('id'))
            )

            all_result = {entry['lesson__title']: entry['count'] for entry in all_tasks_by_lesson}
            return Response({'done': done_result, 'all': all_result}, status=status.HTTP_200_OK)

        elif chart_type == 'category':
            lesson_tasks = self.get_queryset().filter(student=student,
                                                      category__isnull=False,
                                                      due_date__range=(start_date, end_date))

            done_tasks_by_lesson = (
                lesson_tasks.filter(
                    is_done=True
                )
                .values('category__id', 'category__title')
                .annotate(count=Count('id'))
            )

            done_result = {entry['category__title']: entry['count'] for entry in done_tasks_by_lesson}

            all_tasks_by_lesson = (
                lesson_tasks
                .values('category__id', 'category__title')
                .annotate(count=Count('id'))
            )

            all_result = {entry['category__title']: entry['count'] for entry in all_tasks_by_lesson}
            return Response({'done': done_result, 'all': all_result}, status=status.HTTP_200_OK)

        elif chart_type == 'weekday':
            all_tasks = self.get_queryset().filter(student=student,
                                                   due_date__range=(start_date, end_date))

            done_tasks_by_weekday = (
                all_tasks.annotate(
                    weekday=ExtractWeekDay('due_date'))  # Extract the day of the week (1=Sunday, 7=Saturday)
                .values('weekday')
                .annotate(count=Count('id'))
                .order_by('weekday')
            )
            result = {entry['weekday']: entry['count'] for entry in done_tasks_by_weekday}

            # add zero values for missing days
            for i in range(1, 8):
                if i not in result:
                    result[i] = 0

            # sort the result
            result = {k: result[k] for k in sorted(result)}
            return Response(result, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid chart type'}, status=status.HTTP_400_BAD_REQUEST)
