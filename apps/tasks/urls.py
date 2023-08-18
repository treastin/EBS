from django.conf.urls import url

from .views import NewTaskView, MyTaskView, CompletedTaskView, \
    ChangeOwnerView, CompleteTaskView, AllTasksView, GetTasksView, \
    RemoveTaskView, NewCommnetView, GetCommentsView, SearchTaskView

# from rest_framework.routers import DefaultRouter
# from apps.tasks.views import TaskViewSet

# router = DefaultRouter()
# router.register(r'ytasks', TaskViewSet, basename='ytasks')

urlpatterns = [
    url(r'ntask', NewTaskView.as_view()),
    url(r'mytasks', MyTaskView.as_view()),
    url(r'completed', CompletedTaskView.as_view()),
    url(r'complete', CompleteTaskView.as_view()),
    url(r'chown', ChangeOwnerView.as_view()),
    url(r'tasks', AllTasksView.as_view()),
    url(r'gettask', GetTasksView.as_view()),
    url(r'rmtask', RemoveTaskView.as_view()),
    url(r'task/ncomment', NewCommnetView.as_view()),
    url(r'task/comments', GetCommentsView.as_view()),
    url(r'search', SearchTaskView.as_view())
    # *router.urls
]
