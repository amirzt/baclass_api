from rest_framework import serializers

from Task.models import Lesson, Task, Category


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()
    category = CategorySerializer()

    class Meta:
        model = Task
        fields = '__all__'


class AddTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['due_date', 'lesson', 'category', 'description', 'due_time', 'time', 'question', 'is_done']
        extra_kwargs = {
            'due_date': {'error_messages': {'required': "Due date is required."}},
        }

    def save(self, **kwargs):
        student = self.context['student']
        due_date = self.validated_data.pop('due_date')

        task = Task(student=student, due_date=due_date, **self.validated_data)
        task.save()
        return task

    def validate(self, data):
        if 'due_date' not in data:
            raise serializers.ValidationError({"due_date": "This field is required."})

        required_fields = ['lesson', 'category', 'description']
        if not any(field in data for field in required_fields):
            raise serializers.ValidationError(
                f"At least one of {', '.join(required_fields)} must be provided."
            )
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'lesson':
                setattr(instance, attr, Lesson.objects.get(id=value))
            elif attr == 'category':
                setattr(instance, attr, Category.objects.get(id=value))
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
