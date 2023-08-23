import json

from django.test import TestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestUser(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.token_access = None
        self.token_refresh = None

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

        data = json.dumps({
            "email": "user@testing.com",
            "password": "HardPass"
        })

        response_login = self.client.post('/user/login',
                                    data=data,
                                    content_type="application/json", )

        self.token_access = response_login.data['access']
        self.token_refresh = response_login.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_access}')

        self.assertEqual(response_login.status_code, 200)

        response_getuser = self.client.get('/user/')

        self.assertEqual(response_getuser.status_code, 200)
