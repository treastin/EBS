from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import UserSerializer, UserListSerializer
from apps.accounts.models import User


class UserViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = UserListSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['POST'], permission_classes=(AllowAny,), serializer_class=UserSerializer)
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Get password from validated data
        password = validated_data.pop("password")

        # Create user
        user = User.objects.create(
            **validated_data,
        )

        # Set password
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)

        response = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(response)
