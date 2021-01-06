from .tests_setup import TestSetUp
from allauth.account.models import EmailAddress


class TestViews(TestSetUp):


    def test_registration_uncorrect(self):

        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)


    def test_registration_correct(self):

        res = self.client.post(self.register_url,
            self.user_data, format='json')
        self.assertEqual(res.status_code, 201)


    def test_unverified_e_login(self):

        self.client.post(self.register_url,
            self.user_data, format='json')
        res = self.client.post(self.login_url, {'username':self.user_data['username'],
            'password':self.user_data["password1"]}, format='json')
        self.assertEqual(res.data['email'], '__EMAIL_NOT_CONFIRMED__')
        self.assertEqual(res.status_code, 400)


    def test_verified_e_login(self):

        response = self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.user_data['email']
        user = EmailAddress.objects.get(email=email)
        user.verified = True
        user.save()
        res = self.client.post(self.login_url, {'username':self.user_data['username'],
            'password':self.user_data["password1"]}, format='json')
        self.assertEqual(res.data['user']['account_type'], '__ORGANIZATION__')
        self.assertEqual(res.status_code, 200)


    def test_registration_already_registered(self):

        self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.user_data['email']
        user = EmailAddress.objects.get(email=email)
        user.verified = True
        user.save()
        res = self.client.post(self.register_url,
            self.user_data, format='json')
        self.assertEqual(res.data['email'][0], '__ALREADY_REGISTERED__')
        self.assertEqual(res.status_code, 400)


    def test_repeat_email_send_correct(self):

        self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.user_data['email']
        res = self.client.post(self.repeat_email_send,
            {'data':email}, format='json')
        self.assertEqual(res.data['email'], 'sended')
        self.assertEqual(res.status_code, 200)


    def test_repeat_email_send_incorrect(self):

        response = self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.user_data['email']
        user = EmailAddress.objects.get(email=email)
        user.verified = True
        user.save()
        res = self.client.post(self.login_url, {'username':self.user_data['username'],
            'password':self.user_data["password1"]}, format='json')
        self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.fake.email()
        res = self.client.post(self.repeat_email_send,
            {'data':email}, format='json')
        self.assertEqual(res.data['email'], '__WRONG_DATA__')


    def test_email_already_confirmed(self):

        response = self.client.post(self.register_url,
            self.user_data, format='json')
        email = self.user_data['email']
        user = EmailAddress.objects.get(email=email)
        user.verified = True
        user.save()
        res = self.client.post(self.login_url, {'username':self.user_data['username'],
            'password':self.user_data["password1"]}, format='json')
        self.client.post(self.register_url,
            self.user_data, format='json')
        res = self.client.post(self.repeat_email_send,
            {'data':email}, format='json')
        self.assertEqual(res.data['email'], '__ALREADY_CONFIRMED__')
