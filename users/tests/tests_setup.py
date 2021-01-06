from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker

class TestSetUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('users:knox_register')
        self.login_url = reverse('users:knox_login')
        self.logout_url = reverse('users:knox_logout')
        self.repeat_email_send = reverse('users:repeat_email_message_url')
        self.fake = Faker()
        self.user_data={
            "username":"testemail",
            "email":"testemail@mail.ru",
            "password1": "superpass",
            "password2": "superpass",
            "account_type": "__ORGANIZATION__"
        }


        return super().setUp()

    def tearDown(self):
        return super().tearDown()
