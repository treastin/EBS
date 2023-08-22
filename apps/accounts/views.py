from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import UserSerializer, UserListSerializer
from apps.accounts.models import User

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


    def list(self, request):
        users_data = UserListSerializer(User.objects.all(), many=True, ).data
        return Response(users_data)

    @action(detail=False, methods=['POST'],permission_classes=(AllowAny,))
    def register(self, request):
        validated_data = self.request.data

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
