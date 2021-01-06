from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from recruiters.filtersets import RecruitersFilters
from recruiters.serializers import RecruiterPublicInfoSerializer, RecruiterInfoSerializer

__all__ = ['RecruiterReadOnlyView', 'RecruiterDetailedReadOnlyView']


class RecruiterReadOnlyView(ReadOnlyModelViewSet):
    """
    Получение данных аккаунта организации.
    Полностью публичная часть.
    А так же список не публичной части.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = RecruiterPublicInfoSerializer
    queryset = get_user_model().active_recruiters_accounts.order_by('-updated_at')

    filterset_class = RecruitersFilters


class RecruiterDetailedReadOnlyView(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Получение данных организации.
    Для авторизованных пользователей.
    """
    serializer_class = RecruiterInfoSerializer
    queryset = get_user_model().active_recruiters_accounts.order_by('-updated_at')
