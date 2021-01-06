from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url, reverse
from allauth.utils import build_absolute_uri
from users.tasks import send_message
from knox.models import AuthToken
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status
from django import forms
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from users.serializers import GeneralAccountSerializer

def create_knox_token(token_model, user, serializer):
    """ Создание knox токена """

    token = AuthToken.objects.create(user=user)
    return token

from rest_auth.registration.views import RegisterView, VerifyEmailView


def get_email_confirmation_url_override(self, request, emailconfirmation):

    url = reverse("users:account_confirm_email", args=[emailconfirmation.key])
    ret = build_absolute_uri(request, url)
    return ret

DefaultAccountAdapter.get_email_confirmation_url = get_email_confirmation_url_override

def respond_email_verification_sent_override(self, request, user):
        return HttpResponseRedirect(reverse("users:account_email_verification_sent"))

DefaultAccountAdapter.respond_email_verification_sent = respond_email_verification_sent_override

def get_signup_redirect_url_override(self, request):
    return resolve_url('users:knox_register')

DefaultAccountAdapter.get_signup_redirect_url = get_signup_redirect_url_override

def send_mail_override(self, template, email, context):
    """ Формирование урла для перехода с почты и создание таска для Celery """

    subject = 'Подтверждение регистрации на Openmind'
    account_confirm_email = settings.AUTH_COMPLETE_URL
    context['activate_url'] = f'{settings.BASE_URL}{account_confirm_email}{context["key"]}'
    send_message.delay(subject, context['activate_url'], email)

DefaultAccountAdapter.send_mail = send_mail_override

@swagger_auto_schema(request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['key'],
                             properties={
                                 'key': openapi.Schema(type=openapi.TYPE_STRING)
                             },
                         ), responses={'200': '{"email":"confirmed", "token":"token"}'},
                         operation_description='POST принимает key из письма для подтверждения регистрации')
def register_create_override(self, request, *args, **kwargs):

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    data = GeneralAccountSerializer(
        user
    ).data
    return Response(data,
                    status=status.HTTP_201_CREATED,
                    headers=headers)

RegisterView.create = register_create_override
