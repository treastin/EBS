from datetime import timedelta, datetime

from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet, mixins, GenericViewSet, ModelViewSet
# Apps models and serializers
from apps.tasks.documents import TaskDocument
from apps.tasks.models import Task, Comment, TimeLog, Timer
from apps.tasks.serializers import (
    TaskSerializer, TaskWithDurationSerializer, CommentSerializer,
    TimelogSerializer, TimerSerializer, TaskDocumentSerializer)
from config.settings import CACHE_TTL

# Elasticsearch_dsl_drf
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT, LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE,
    STRING_LOOKUP_FILTERS,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ['title']
    filterset_fields = ('status', 'assigned_to')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['list', 'top20']:
            return qs.annotate(total_duration=(Sum('timelog_task__duration'))).order_by('-id')
        return qs

    def get_serializer_class(self):
        if self.action in ['list', 'top20']:
            return TaskWithDurationSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        task_reassigned = False
        assigned_to = serializer.validated_data.get('assigned_to')

        if assigned_to and serializer.instance.assigned_to != assigned_to:
            task_reassigned = True

        serializer.save()

        if task_reassigned:
            send_mail(
                recipient_list=[serializer.validated_data['assigned_to']],
                subject="You have ben assigned a new task!",
                message=f"You have ben assigned a new task!\n The new task is \"{serializer.instance.title}\".",
                from_email=None,
            )

    @method_decorator(cache_page(CACHE_TTL))
    @action(detail=False, methods=['GET'])
    def top20(self, response, *args, **kwargs):
        this_month = datetime.now().replace(day=1).date()
        tasks = (self.get_queryset()
                 .filter(timelog_task__started_at__gte=this_month)
                 .filter(total_duration__isnull=False)
                 .order_by('-total_duration')[:20]
                 )
        tasks_data = self.get_serializer(tasks, many=True).data
        return Response(tasks_data)

    @action(detail=True, methods=['POST'])
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Task.Status.COMPLETED:
            instance.status = Task.Status.COMPLETED
            instance.save()
            send_mail(
                recipient_list=[instance.assigned_to.email],
                subject="Your task is now complete!",
                message=f"The task \"{instance.title}\".",
                from_email=None,
                fail_silently=True,
            )
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def start(self, request, pk=None, *args, **kwargs):
        instance = Timer.objects.get_or_create(user=self.request.user, task_id=pk)[0]
        instance.start()
        serializer = TimerSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def stop(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(Timer.objects.all(), user=self.request.user, task_id=pk)
        timelog = instance.stop()
        serializer = TimelogSerializer(timelog)
        return Response(serializer.data)


class CommentViewSet(ViewSet,
                     GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['task']
    search_fields = ['text']

    def perform_create(self, serializer):
        send_mail(
            subject="Your task has a new comment.",
            message=f"Hi, {self.request.user.first_name}.\n"
                    f"The task {serializer.validated_data['task'].title} has a new comment.",
            recipient_list=[self.request.user.email],
            from_email=None,
            fail_silently=True
        )
        serializer.save()


class TimelogViewSet(ViewSet,
                     GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    queryset = TimeLog.objects.all()
    serializer_class = TimelogSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['task']

    @action(detail=False, methods=['GET'])
    def mytime(self, request, *args, **kwargs):
        last_day_of_last_month = datetime.now().replace(day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1, hour=0, minute=0, second=0)

        tasks_by_user = TimeLog.objects.filter(
            user=self.request.user,
            started_at__gt=first_day_of_last_month,
            started_at__lt=last_day_of_last_month
        )

        total = tasks_by_user.aggregate(total=Sum('duration')).get('total') or 0

        return Response({'total_time': total})


class ESPaginatedViewSet(BaseDocumentViewSet):
    document = TaskDocument
    serializer_class = TaskDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
    ]
    search_fields = (
        'title',
        'comment.text',
    )

    filter_fields = {
        'id': {
            'field': 'id',
            # Note, that we limit the lookups of id field in this example,
            # to `range`, `in`, `gt`, `gte`, `lt` and `lte` filters.
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'comment': {
            'field': 'comment.text.raw',
            'lookups': [
                STRING_LOOKUP_FILTERS
            ],
        },
        'title': {
            'field': 'title',
            'lookups': [
                STRING_LOOKUP_FILTERS
            ]
        }
    }
    ordering_fields = {
        'id': 'id'
    }
    ordering = ['-id']

