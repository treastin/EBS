import http

from django.views.generic import DeleteView
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from apps.tasks.models import Task, Comment
from drf_util.decorators import serialize_decorator
from rest_framework.generics import GenericAPIView

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.helpers import send_mail
from apps.common.gmail import send_gmail

from apps.tasks.serializers import TaskSerializer, NewTaskSerializer, MyTaskSerializer, TaskByidSerializer, \
    CommentSerializer, CommentByIdSerializer, TaskChangeSerializer, SearchTaskSerializer


# Create your views here.

# Using ROUTER
#
# class TaskViewSet(ModelViewSet):
#     serializer_class = TaskSerializer
#     permission_classes = (IsAuthenticated,)
#     queryset = Task.objects.all()
#
#     # def retrieve(self, request, pk=None, *args, **kwargs):
#     #     task = Task.objects.filter(id=pk)
#     #     task_data = TaskSerializer(task,).data
#     #     task_data.update({'id': pk})
#     #
#     #     return Response(task_data)
#     #
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

class AllTasksView(GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tasks = Task.objects.all()
        tasks_data = TaskSerializer(tasks, many=True).data

        return Response(tasks_data)


class GetTasksView(GenericAPIView):
    serializer_class = TaskByidSerializer
    permission_classes = (IsAuthenticated,)

    @serialize_decorator(TaskByidSerializer)
    def post(self, request):
        tasks = Task.objects.get(pk=self.request.data['id'])
        tasks_data = TaskSerializer(tasks, ).data

        return Response(tasks_data)


class NewTaskView(GenericAPIView):
    serializer_class = NewTaskSerializer

    permission_classes = (IsAuthenticated,)

    @serialize_decorator(NewTaskSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        task = Task.objects.create(**validated_data, owner=self.request.user, status='In progress')
        task.save()

        response = {
            'id': task.id
        }

        try:
            send_mail(
                user=task.owner.email,
                subject="You have ben assigned a new task!",
                message=f"You have ben assigned a new task!\n The new task is \"{task.title}\".")
        except:
            pass

        return Response(response)


class MyTaskView(GenericAPIView):
    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated,)

    # @serialize_decorator(MyTaskSerializer)
    def get(self, request):
        mytasks = Task.objects.filter(owner=self.request.user, )
        mytasks_data = MyTaskSerializer(mytasks, many=True).data

        return Response(mytasks_data)


class CompletedTaskView(GenericAPIView):
    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated,)

    # @serialize_decorator(MyTaskSerializer)
    def get(self, request):
        completed_tasks = Task.objects.filter(status='Completed', )
        completed_tasks_data = MyTaskSerializer(completed_tasks, many=True).data

        return Response(completed_tasks_data)


class ChangeOwnerView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskChangeSerializer

    def post(self, request, ):
        Task.objects.filter(pk=self.request.data['id']).update(owner=self.request.data['owner'])

        task = Task.objects.get(pk=self.request.data['id'])

        try:
            send_mail(
                user=task.owner.email,
                subject="You have ben assigned a new task!",
                message=f"You have ben assigned a new task!\n The new task is \"{task.title}\".")
        except Exception as e:
            print(e)
            pass

        return Response({}, status=http.HTTPStatus.OK)


class CompleteTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskByidSerializer

    def post(self, request, ):
        task_id = self.request.data['id']
        Task.objects.filter(pk=task_id).update(status='Completed')

        task = Task.objects.get(pk=self.request.data['id'])

        send_mail(
            user=task.owner.email,
            subject='Your task is now complete!',
            message=f'The task \"{task.title}\" is completed.'
        )

        return Response({}, status=http.HTTPStatus.OK)


class RemoveTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskByidSerializer

    def post(self, request, ):
        Task.objects.filter(pk=self.request.data['id']).delete()
        return Response({}, status=http.HTTPStatus.OK)


class NewCommnetView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    @serialize_decorator(CommentSerializer)
    def post(self, request, ):
        validated_data = request.serializer.validated_data

        comment = Comment.objects.create(**validated_data)
        comment.save()

        task = Task.objects.get(pk=validated_data['task'].id)

        send_mail(
            user=task.owner.email,
            subject='Your task got a new comment!',
            message=f'The task \"{task.title}\" got a new comment :\n {validated_data["text"]}'
        )
        return Response({'id': comment.id}, status=http.HTTPStatus.CREATED)


class GetCommentsView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentByIdSerializer

    @serialize_decorator(CommentByIdSerializer)
    def post(self, request):
        validate_data = request.serializer.validated_data

        comments = Comment.objects.filter(**validate_data)
        comments_data = CommentSerializer(comments, many=True).data

        return Response(comments_data, status=http.HTTPStatus.OK)


class SearchTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchTaskSerializer

    @serialize_decorator(SearchTaskSerializer)
    def post(self, request):
        validate_data = request.serializer.validated_data

        tasks = Task.objects.filter(title__contains=validate_data['title'])
        tasks_data = TaskSerializer(tasks, many=True).data

        return Response(tasks_data, status=http.HTTPStatus.OK)
