from django.db.models import Sum
from apps.tasks.models import Task, Comment, TimeLog, Timer
from rest_framework import serializers
from django.db.models import DurationField


class TaskSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField(default=0)

    class Meta:
        model = Task
        fields = [
            'id',
            'description',
            'status',
            'assigned_to',
            'created_by',
            'total_duration',
        ]

        read_only_fields = [
            'id',
            'created_by',

        ]
        write_only_fields = [
            'id',
            'assigned_to',
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


class Top20Serializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField(default=0)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'total_duration'
        ]
        read_only_fields = [
            'id',
        ]



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
