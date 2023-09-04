from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, mixins, GenericViewSet

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404

from datetime import timedelta, datetime

from config.settings import CACHE_TTL

from apps.tasks.models import Task, Comment, TimeLog, Timer
from apps.tasks.serializers import AssignSerializer, TimerSerializer, \
    TaskSerializer,TaskWithDurationSerializer, CommentSerializer, Top20Serializer, \
    MyTaskSerializer, TimelogSerializer


class TaskViewSet(ViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Task.objects.with_total_duration()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ['title']
    filterset_fields = ('status', 'assigned_to')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['list']:
            qs.annotate(total_duration=(Sum('timelog_task__duration'))).order_by('-id')
            return qs
        return qs

    def get_serializer_class(self):
        if self.action in ['list']:
            return TaskWithDurationSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'completed'
        instance.save()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    @action(detail=False, serializer_class=Serializer)
    def mytasks(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(assigned_to=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MyTaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MyTaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'], serializer_class=AssignSerializer)
    def assign(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset().get(id=pk)
        serializer = self.get_serializer(instance=instance, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CommentViewSet(ViewSet,
                     GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin):
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
            recipient_list=[*self.request.user.email],
            from_email=None
        )


class TimelogViewSet(ViewSet,
                     GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    queryset = TimeLog.objects.all()
    serializer_class = TimelogSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['task']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['top20']:
            qs.annotate(total_duration=(Sum('timelog_task__duration'))).order_by('-id')
            return qs
        return qs

    @action(detail=False)
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

    @method_decorator(cache_page(CACHE_TTL))
    @action(detail=False)
    def top20(self, response, *args, **kwargs):
        this_month = datetime.now().replace(day=1).date()
        tasks = (self.get_queryset()
                 .filter(timelog_task__started_at__gte=this_month)
                 .filter(total_duration__isnull=False)
                 .order_by('-total_duration')[:20]
                 )
        tasks_data = Top20Serializer(tasks, many=True).data
        return Response(tasks_data)


class TimerViewSet(ViewSet, GenericViewSet):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def start(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset().get_or_create(user=self.request.user, task_id=pk)[0]
        instance.start()
        return Response()

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def stop(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), user=self.request.user, task_id=pk)
        difference = (timezone.now() - instance.started_at).total_seconds() // 60
        instance.stop()
        return Response(
            {'details': f'Current task had duration of : {int(difference)} min.'})
