from django.db.models import Sum
from apps.tasks.models import Task, Comment, Timelog
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'

        read_only_fields = [
            'id',
            'created_by',
        ]


class TaskListSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    time_passed = serializers.SerializerMethodField()

    def get_time_passed(self, task):
        time_passed = task.timelog_set.aggregate(total=Sum('duration')).get('total')
        return time_passed or 0

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'time_passed',
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    assigned_to = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = '__all__'


class TaskAssignSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    assigned_to = serializers.IntegerField()

    class Meta:
        model = Task
        fields = (
            'id',
            'assigned_to'
        )


class MyTaskSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'task',
            'text',
        ]


class SearchTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title'
        ]


class StartTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = [
            'id',
            'task',
        ]


class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = '__all__'


class Top20Serializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    time_passed = serializers.SerializerMethodField()

    def get_time_passed(self, task):
        time_passed = task.timelog_set.aggregate(total=Sum('duration')).get('total')
        return time_passed or 0

    class Meta:
        model = Task
        fields = [
            'id',
            "title",
            "time_passed",
        ]


class TimelogSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    assigned_to = serializers.ReadOnlyField()

    class Meta:
        model = Timelog
        fields = '__all__'
