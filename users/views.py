from django.shortcuts import render
"""
Обработчики управления пользователями.
"""
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from .serializers import KnoxSerializer
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from users.utils import *
from rest_auth.app_settings import TokenSerializer
from rest_framework.exceptions import APIException
from rest_framework.serializers import ValidationError
from rest_auth.registration.views import VerifyEmailView
from users.serializers import GeneralAccountSerializer

class LoginPageView(LoginView):
    """
    Страница формы входа.
    """
    template_name = 'index.html'



class LogoutViewPageView(LogoutView):
    """
    Страница выхода.
    """
    next_page = reverse_lazy('users:login')




class VerifyOverrideView(VerifyEmailView):
    """ Страница подтверждения регистрации """

    @swagger_auto_schema(
                            request_body=openapi.Schema(
                                 type=openapi.TYPE_OBJECT,
                                 required=['key'],
                                 properties={
                                     'key': openapi.Schema(type=openapi.TYPE_STRING)
                                 },
                             ), responses={'200': '{"email":"confirmed", "token":"token"}'},
                             operation_description='POST принимает key из письма для подтверждения регистрации')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        user = confirmation.email_address.user
        if user.is_confirmed():
            raise ValidationError('__ALREADY_REGISTERED__')
        else:
            _, token = create_knox_token(None, confirmation.email_address.user, None)
            confirmation.confirm(self.request)
            return Response({'e-mail': 'confirmed',
                            'token': token,
                            'username': user.username}, status=status.HTTP_200_OK)


class KnoxRegisterView(RegisterView):
    """ Страница регистрации """


    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                        required=['username', 'email', 'password1', 'password2'],
                        properties={
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'password1': openapi.Schema(type=openapi.TYPE_STRING),
                            'password2': openapi.Schema(type=openapi.TYPE_STRING),
                            'account_type': openapi.Schema(type=openapi.TYPE_STRING)
                                   },
                        ), responses={'200': GeneralAccountSerializer()},
    operation_description=
    """POST форма для регистрации аккаунтов, возможные варианты account_type:
    Организация - '\_\_ORGANIZATION\_\_',
    Соискатель - '\_\_HIRER\_\_',
    Наниматель - '\_\_APPLICANT\_\_'
    """)
    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        return response

    def get_response_data(self, user):
        return KnoxSerializer({'user': user, 'token': self.token}).data

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        complete_signup(self.request._request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user


class VerifyView(VerifyEmailView):
    swagger_schema = None

    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        return response
