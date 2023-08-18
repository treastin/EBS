from apps.accounts.models import CustomUser
from drf_util.decorators import serialize_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import UserSerializer, UserListSerializer


class RegisterUserView(GenericAPIView):
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    @serialize_decorator(UserSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        # Get password from validated data
        password = validated_data.pop("password")

        # Create user
        user = CustomUser.objects.create(
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


# class RegisterGenericUserView(GenericAPIView):
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny,)
#
#     def post(self, request):


class UserListView(GenericAPIView):
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        users = CustomUser.objects.all()
        users_data = UserListSerializer(users, many=True, ).data
        return Response(users_data)
