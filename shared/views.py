"""
Обработчики запросов.
"""
from django.contrib.auth.mixins import LoginRequiredMixin


class AuthUserContextMixin(LoginRequiredMixin):
    """
    Миксин для формирования контекста авторизованного пользователя
    """

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        # Просто вынесем пользователя по выше.
        kwargs['user'] = kwargs['view'].request.user
        return kwargs
