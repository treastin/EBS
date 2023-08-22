import http

from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from datetime import timedelta, datetime


from apps.common.helpers import send_mail
from apps.tasks.models import Task, Comment, Timelog
from apps.tasks.serializers import TaskListSerializer, TaskUpdateSerializer, \
    TaskSerializer, TaskAssignSerializer, CommentSerializer, SearchTaskSerializer,\
    Top20Serializer, MyTaskSerializer, TimelogSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskListSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [SearchFilter]
    search_fields = ['title',]

    def get_serializer_class(self):

        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer

        if self.action in ['mytask', 'completed', 'complete']:
            return Serializer

        if self.action in ['assign']:
            return TaskAssignSerializer

        if self.action in ['search']:
            return SearchTaskSerializer

        if self.action in ['list']:
            return TaskListSerializer

        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['POST'])
    def complete(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'completed'
        instance.save()
        send_mail(
            receivers=instance.assigned_to.email,
            subject="You have ben assigned a new task!",
            message=f"You have ben assigned a new task!\n The new task is \"{instance.title}\".")
        return Response(data={'details': 'Task completed'})

    @action(detail=False, serializer_class=Serializer)
    def mytasks(self, request):
        mytasks = Task.objects.filter(assigned_to=self.request.user, )
        mytasks_data = MyTaskSerializer(mytasks, many=True).data
        return Response(data=mytasks_data)

    @action(detail=False, serializer_class=Serializer)
    def completed(self, request):
        completed_tasks = Task.objects.filter(status='completed', )
        completed_tasks_data = TaskSerializer(completed_tasks, many=True).data
        return Response(completed_tasks_data)

    @action(detail=False, methods=['PUT'],  serializer_class=TaskAssignSerializer)
    def assign(self, request):
        Task.objects.filter(pk=self.request.data['id']).update(assigned_to=self.request.data['assigned_to'])
        task = Task.objects.get(pk=self.request.data['id'])
        send_mail(
            receivers=task.assigned_to.email,
            subject="You have ben assigned a new task!",
            message=f"You have ben assigned a new task!\n The new task is \"{task.title}\".")
        return Response({}, status=http.HTTPStatus.OK)

    @action(detail=True)
    def timelog(self, request, pk=None):
        tasks = TimelogSerializer(Timelog.objects.all().filter(task=pk), many=True)
        return Response(data=tasks.data, status=http.HTTPStatus.OK)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        task = Task.objects.get(pk=serializer.data['task'])
        send_mail(
            receivers=task.assigned_to.email,
            subject='Your task got a new comment!',
            message=f'The task \"{task.title}\" got a new comment :\n {serializer.data["text"]}'
        )
        return Response(serializer.data, status=201, headers=headers)


class TimelogViewSet(ModelViewSet):
    serializer_class = TimelogSerializer
    queryset = Timelog.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):

        if self.action in ['set']:
            return TimelogSerializer

        return TimelogSerializer

    @action(detail=True, methods=['POST'])
    def start(self, request, pk=None):
        latest_timelog_exists = self.queryset.filter(task=pk, duration__isnull=True).exists()

        if latest_timelog_exists:
            return Response({'details': 'This task is currently ongoing. '}, status=http.HTTPStatus.BAD_REQUEST)
        else:
            Timelog.objects.create(task_id=pk).save()
            return Response({'details': 'Timelog started.'}, status=http.HTTPStatus.CREATED)

    @action(detail=True, methods=['POST'])
    def stop(self, request, pk=None):
        latest_timelog_q = self.queryset.filter(task=pk, duration__isnull=True)

        try:
            latest_timelog = latest_timelog_q.get()
        except MultipleObjectsReturned:
            return Response({'details': 'The task has more than 1 ongoing timelog.'},
                            status=http.HTTPStatus.MULTIPLE_CHOICES)

        except ObjectDoesNotExist:
            return Response({'details': 'The task has no ongoing timelog.'}, status=http.HTTPStatus.BAD_REQUEST)

        duration = int((timezone.now() - latest_timelog.start).total_seconds() // 60)

        latest_timelog_q.update(duration=duration)

        return Response({'details': f'The duration of the task is {duration} minutes.'}, 200)

    @action(detail=False)
    def mytime(self, request):
        last_day_of_last_month = datetime.now().replace(day=1) - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        tasks_by_user = (Task.objects.filter(
            assigned_to=self.request.user,
            timelog__start__gte=first_day_of_last_month,
            timelog__start__lte=last_day_of_last_month
        ))

        total = tasks_by_user.aggregate(total=Sum('timelog__duration')).get('total')

        return Response({'total_time': total})

    @action(detail=False)
    def top20(self, response):
        last_day_of_last_month = datetime.now().replace(day=1) - timedelta(days=1)
        tasks = (Task.objects
                 .filter(timelog__start__gte=last_day_of_last_month)
                 .annotate(time=Sum('timelog__duration'))
                 .order_by('-time')
                 )

        tasks_data = Top20Serializer(tasks, many=True).data
        return Response(tasks_data)
