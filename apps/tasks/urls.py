from apps.tasks.views import TaskViewSet, CommentViewSet, TimelogViewSet, ESPaginatedViewSet, TaskSearchViewSet

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')
router.register('comment', CommentViewSet, basename='comments')
router.register('timelog', TimelogViewSet, basename='timelog')

router.register('es', ESPaginatedViewSet, basename='es')
router.register('drf', TaskSearchViewSet, basename='search')
urlpatterns = router.urls
