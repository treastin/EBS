from django.db.models import Sum
from apps.tasks.models import Task, Comment, Timelog
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
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
            "description",
            "status",
            "owner",
            "time_passed",
        ]


class NewTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
        ]


class MyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
        ]


class TaskChangeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    owner = serializers.IntegerField()

    class Meta:
        model = Task
        fields = [
            'id',
            'owner',
        ]


class TaskByidSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Task
        fields = [
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


class CommentByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'task',
        ]


class SearchTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
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
