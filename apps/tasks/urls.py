from apps.tasks.views import TaskViewSet, CommentViewSet, TimelogViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')
router.register('comment', CommentViewSet, basename='comments')
router.register('timelog', TimelogViewSet, basename='timelog')
urlpatterns = router.urls
