from django.conf.urls import url

from apps.tasks.views import NewTaskView, MyTaskView, CompletedTaskView, \
    ChangeOwnerView, CompleteTaskView, AllTasksView, GetTasksView, \
    RemoveTaskView, NewCommnetView, GetCommentsView, SearchTaskView, \
    StartTimelogView, StopTimelogView, SetTimelogView, GetTimelogView, \
    GetMyTimelogView, GetTop20View

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
    url(r'search', SearchTaskView.as_view()),
    url(r'timelog/start', StartTimelogView.as_view()),
    url(r'timelog/stop', StopTimelogView.as_view()),
    url(r'timelog/set', SetTimelogView.as_view()),
    url(r'timelog/get', GetTimelogView.as_view()),
    url(r'timelog/last_month', GetMyTimelogView.as_view()),
    url(r'task/top20', GetTop20View.as_view()),
    # *router.urls
]
