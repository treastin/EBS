import json

from django.contrib.auth.hashers import make_password
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserListSerializer


# Create your tests here.


class TestUser(TransactionTestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(email='string@mail.ogg', password=make_password('StrongPassword'))
        self.client.force_authenticate(user=self.user, token=f'Bearer {RefreshToken.for_user(self.user)}')

    def test_register(self):
        data = json.dumps({
            "first_name": "User",
            "last_name": "For Test",
            "email": "user@testing.com",
            "password": "HardPass"})

        response_register = self.client.post('/user/register/',
                                             data=data,
                                             content_type="application/json", )

        self.assertEqual(response_register.status_code, 200)

    def test_login(self):
        data = json.dumps({
            "email": "string@mail.ogg",
            "password": "StrongPassword"
        })

        response_login = self.client.post('/user/login',
                                          data=data,
                                          content_type="application/json", )

        self.assertEqual(response_login.status_code, 200)

        self.token_access = response_login.data['access']
        self.token_refresh = response_login.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_access}')

    def test_get_user(self):

        response_getuser = self.client.get('/user/1/')

        self.assertEqual(response_getuser.status_code, 200, "The user didn't get a list.")

        user_object = User.objects.first()

        self.assertEqual(response_getuser.data["full_name"], UserListSerializer().get_full_name(user_object))

        self.assertEqual(response_getuser.status_code, 200)
