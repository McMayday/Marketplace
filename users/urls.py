"""
Роутер приложения пользователей.
"""
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from .api import repeat_register
from .views import VerifyOverrideView, KnoxRegisterView, VerifyView
from users.api import LoginView, UserData, PublicUserDataViewSet, GetAuthParams
from knox import views as knox_views

from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter()
router.register(r'data', UserData)
router.register(r'data/public', PublicUserDataViewSet)



urlpatterns = [  # pylint: disable=invalid-name
    url(r'login/', LoginView.as_view(), name='knox_login'),
    url(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    url(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    url(r'oauth/getclientid/(?P<oauth_provider>.+)$', GetAuthParams.as_view(), name='get_client_id'),
    path('registration/', KnoxRegisterView.as_view(), name='knox_register'),
    path('account-email-verification/', VerifyView.as_view(),name='account_email_verification_sent'),
    path('account-confirm-email/repeat', csrf_exempt(repeat_register), name='repeat_email_message_url'),
    path('account-confirm-email/<str:key>/', VerifyOverrideView.as_view(),
        name='account_confirm_email'),
    path('oauth/authorize/', include(('rest_social_auth.urls_knox', 'account'), namespace='account')),
]
