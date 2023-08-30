from django.contrib.auth.hashers import make_password
from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserListSerializer


class TestUser(TransactionTestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(first_name='User',
                                        last_name='For Testing',
                                        email='string@mail.ogg',
                                        password=make_password('StrongPassword'))
        self.client.force_authenticate(user=self.user, token=f'Bearer {RefreshToken.for_user(self.user)}')

    def test_register(self):
        data = {
            "first_name": "User",
            "last_name": "For Test",
            "email": "user@testing.com",
            "password": "HardPass"}

        response_register = self.client.post(reverse('user-register'), data=data)

        self.assertEqual(response_register.status_code, 200)

    def test_login(self):
        data = {
            "email": "string@mail.ogg",
            "password": "StrongPassword"
        }

        response_login = self.client.post(reverse('token_obtain_pair'), data=data)

        self.assertEqual(response_login.status_code, 200)

        self.token_access = response_login.data['access']
        self.token_refresh = response_login.data['refresh']

    def test_get_user(self):
        user = User.objects.create(first_name='User',
                            last_name='For Testing',
                            email='strings2@mail.ogg',
                            password=make_password('StrongPassword'))

        url = reverse('user-detail', args=[user.id])
        response_getuser = self.client.get(url)

        self.assertEqual(response_getuser.status_code, 200, "The endpoint did not return user{id:1}")

        user_object = User.objects.first()

        self.assertEqual(response_getuser.data["full_name"], UserListSerializer().get_full_name(user_object))

        self.assertEqual(response_getuser.status_code, 200)
