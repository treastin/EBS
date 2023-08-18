from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import RegisterUserView, UserListView

urlpatterns = [
    path("auth/register", RegisterUserView.as_view(), name="token_register"),
    path("auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path('getusers', UserListView.as_view(), name="User_list")
]
