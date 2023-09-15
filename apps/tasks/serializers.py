from datetime import timedelta

from drf_util.serializers import PaginatorSerializer, ElasticFilterSerializer

from apps.tasks.models import Task, Comment, TimeLog, Timer
from apps.tasks.documents import TaskDocument
from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer


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


class TaskDocumentSerializer(DocumentSerializer):
    class Meta:
        document = TaskDocument
        fields = '__all__'


class GlobalSearchFilterElasticSerializer(PaginatorSerializer, ElasticFilterSerializer):
    search = serializers.CharField(required=False)
    task_id = serializers.IntegerField(required=False)
    task_name = serializers.CharField(required=False)
    comments = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
    ordering = serializers.CharField(required=False)

    class Meta:
        model = Task
        fields = [
            'search',
            'task_id',
            'task_name',
            'comments',
            'ordering',
        ]


class CommentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


class TasksDocumentSerializer(serializers.ModelSerializer):
    comment = CommentSerializer()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'comment'
        ]

