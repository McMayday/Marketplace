import uuid
from drf_yasg import openapi
from django.contrib.auth import login, get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, response, mixins
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from knox.views import LoginView as KnoxLoginView
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.throttling import AnonRateThrottle
from app.settings import SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
from users.filterset import UserInfoFilterSet
from users.serializers import GeneralAccountSerializer, PublicUserInfoSerializer, OauthParamsSerializer
from allauth.account.models import EmailAddress, EmailConfirmation
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth.models import User


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
        request_body=AuthTokenSerializer(),
        responses={200: GeneralAccountSerializer()}
    )
    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        e_confirm = self.credential(user)
        if e_confirm != True:
            return e_confirm
        login(request, user)
        return super(LoginView, self).post(request, format=None)

    def credential(self, username):
        try:
            user = EmailAddress.objects.get(user = username)
        except User.DoesNotExist:
            raise AuthenticationFailed('No such user')
        if user.verified == False:
            return response.Response({'email': '__EMAIL_NOT_CONFIRMED__'}, status=status.HTTP_400_BAD_REQUEST)
        return True


class UserData(GenericViewSet):
    """
    Персональные данные аккаунта.
    """
    serializer_class = GeneralAccountSerializer
    queryset = get_user_model().objects.filter(is_active=True)

    @swagger_auto_schema(
        methods=['get', 'patch']
    )
    @action(detail=False, methods=['get', 'patch'], url_path='user-data')  # detail=False чтобы не было id в урле
    def user_data(self, request):
        if request.method == "GET":
            serializer = GeneralAccountSerializer(request.user)
            return response.Response(serializer.data)
        elif request.method == "PATCH":
            serializer = GeneralAccountSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)


class PublicUserDataViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """
    Данные для публичного показа
    Выводятся только аккакаунты с типом \_\_APPLICANT\_\_
    """
    permission_classes = (permissions.AllowAny,)

    filterset_class = UserInfoFilterSet

    serializer_class = PublicUserInfoSerializer
    queryset = get_user_model().active_applicants_accounts.order_by('-date_joined')


class GetAuthParams(APIView):
    """
    Получение параметров Oauth провайдера.
    """
    permission_classes = (permissions.AllowAny,)

    provider_client_id_map = {
        'google-oauth2': SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    }

    @swagger_auto_schema(
        responses={200: OauthParamsSerializer()}
    )
    def get(self, request, oauth_provider):
        state = f'{str(uuid.uuid4())}_{oauth_provider}'
        try:
            client_id = self.provider_client_id_map[oauth_provider]
        except KeyError:
            raise ValidationError('Bad provider name')
        return response.Response({
            "state": state,
            "client_id": client_id
        })


class OncePerMinuteAnonThrottle(AnonRateThrottle):
        rate = '1/minute'


@swagger_auto_schema(methods=['post'],
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['e-mail'],
                             properties={
                                 'email': openapi.Schema(type=openapi.TYPE_STRING)
                             },
                         ), responses={'200': '{"email":"sended"}'},
                         operation_description='POST повторно отправляет e-mail на почту, пример запроса: {"data":"abc@mail.ru"}')
@api_view(['POST'])
@parser_classes((JSONParser,))
@throttle_classes([OncePerMinuteAnonThrottle])
@permission_classes([permissions.AllowAny])
def repeat_register(request):
    """ Повторная отправка e-mail """
    try:
        user = EmailAddress.objects.get(email__iexact = request.data['data'])
    except:
        return response.Response({'email': '__WRONG_DATA__'}, status=status.HTTP_400_BAD_REQUEST)
    if user.verified == False:
        x = user.send_confirmation()
        return response.Response({'email': 'sended'}, status=status.HTTP_200_OK)
    else:
        return response.Response({'email': '__ALREADY_CONFIRMED__'}, status=status.HTTP_400_BAD_REQUEST)
