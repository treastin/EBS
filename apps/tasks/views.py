import http

from rest_framework import status
from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, mixins, GenericViewSet

from django.db.models import Sum, Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from datetime import timedelta, datetime

from apps.tasks.models import Task, Comment, TimeLog, Timer
from apps.tasks.serializers import AssignSerializer, TimerSerializer, \
    TaskSerializer, CommentSerializer, Top20Serializer, \
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

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'completed'
        instance.save()
        return Response(data={'details': 'Task completed'})

    @action(detail=False, serializer_class=Serializer)
    def mytasks(self, request, *args, **kwargs):
        queryset = self.queryset.filter(assigned_to=self.request.user)
        serializer = MyTaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'], serializer_class=AssignSerializer)
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=self.request.data, instance=instance)
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

    def perform_create(self, serializer):
        send_mail(
            subject="Your task has a new comment.",
            message=f"Hi, {self.request.user.first_name}.\nThe task {serializer.validated_data['task'].title} has a new comment.",
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

    @action(detail=False)
    def top20(self, response, *args, **kwargs):
        this_month = datetime.now().replace(day=1).date()
        tasks = (Task.objects.with_total_duration()
                 .filter(task_timer__started_at__gte=this_month)
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
        instance = self.queryset.get_or_create(user=self.request.user, task_id=pk)[0]
        instance.start()
        return Response({})

    @action(detail=True, methods=['POST'], serializer_class=Serializer)
    def stop(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.queryset.get(user=self.request.user, task_id=pk)
        except ObjectDoesNotExist:
            return Response({'details': 'There is no ongoing timer.'}, status=400)

        difference = (timezone.now() - instance.started_at).total_seconds() // 60
        instance.stop()
        return Response(
            {'details': f'Current task had duration of : {int(difference)} min.'})
