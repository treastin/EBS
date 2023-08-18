from apps.tasks.models import Task, Comment
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    task_id = serializers.ReadOnlyField(source='get_pk', )

    class Meta:
        model = Task
        fields = [
            'id',
            "task_id",
            "title",
            "description",
            "status",
            "owner",
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
