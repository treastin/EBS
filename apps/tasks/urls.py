from apps.tasks.views import TaskViewSet, CommentViewSet, TimelogViewSet, SearchTasks

from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')
router.register('comment', CommentViewSet, basename='comments')
router.register('timelog', TimelogViewSet, basename='timelog')
elasticsearch = path('search/<str:query>/', SearchTasks.as_view())
urlpatterns = router.urls
urlpatterns.append(elasticsearch)
