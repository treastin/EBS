from datetime import timedelta

from drf_util.serializers import PaginatorSerializer, ElasticFilterSerializer

from apps.tasks.models import Task, Comment, TimeLog, Timer
from apps.tasks.documents import TaskDocument
from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

SEARCH_FIELDS = ['title', 'comment.text']


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


class CommentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


class TaskESSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'comment'
        ]


class SearchFilterElasticSerializer(PaginatorSerializer, ElasticFilterSerializer):
    search = serializers.CharField(required=False)
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    comments = serializers.CharField(required=False)

    def get_filter(self):
        fields = self.get_fields()
        for field_name, field_instance in fields.items():
            function_name = 'filter_' + field_name
            if not hasattr(self, function_name) and field_name not in (*PaginatorSerializer().get_fields(), 'ordering'):
                setattr(self, 'filter_' + field_name, self.make_function(field_name, field_instance))
        return super().get_filter()

    def make_function(self, field_name, field_instance): # noqa
        if isinstance(field_instance, serializers.PrimaryKeyRelatedField):
            field_name += '.id'
            return lambda value: {'term': {field_name: value.id if '.id' in field_name else value}}

    def set_ordering(self, value):
        order = 'asc'
        if value.startswith('-'):
            value = value[1:]
            order = 'desc'
            self.sort_criteria = [{
                value: order
            }]

    def filter_search(self, value): # noqa
        return {
            'multi_match': {
                'query': value, 'fields': SEARCH_FIELDS
            }
        }

    def filter_comments(self, value): # noqa
        return {
            'match': {
                'comments.text': {
                    'query': value
                }
            }
        }

    def filter_title(self, value): # noqa
        return {
            'match': {
                'title': {
                    'query': value
                }
            }
        }

    def filter_id(self, value): # noqa
        return {
            'match': {
                'id': value
            }
        }

