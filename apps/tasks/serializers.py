from datetime import timedelta
from apps.tasks.models import Task, Comment, TimeLog, Timer
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

        read_only_fields = [
            'id',
            'created_by',

        ]
        write_only_fields = [
            'id',
            'assigned_to',
        ]


class TaskWithDurationSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField(default=timedelta(), read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'total_duration',
        ]
        read_only_fields = [
            'id',
        ]
        write_only_fields = [
            'id',
        ]


class AssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'assigned_to',
        ]


class MyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
        ]
        read_only_fields = [
            'id',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'task',
            'text',
        ]


class StartTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = [
            'id',
            'task',
        ]


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'


class TimelogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'
        read_only_fields = [
            'created_by',
            'status',
            'assigned_to',
        ]


class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = '__all__'

