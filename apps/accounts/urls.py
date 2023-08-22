from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet, "user")

urlpatterns = router.urls

urlpatterns += [
    path("user/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
