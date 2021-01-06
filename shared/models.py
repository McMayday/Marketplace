"""
Модели общей функциональности.
"""
import uuid

from django.conf import settings
from django.db.models import JSONField
from django.db import models


class AvailableObjectsManager(models.Manager):
    """
    Менеджер для работы только "не удаленными объектами".
    """
    def get_queryset(self):
        return super().get_queryset().exclude(is_deleted=True)


class BaseModel(models.Model):
    """
    Базовая модель, которая содержит общий набор полей для всех моделей проекта.
    """
    objects = models.Manager()
    existing_objects = AvailableObjectsManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='идентификатор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_deleted = models.BooleanField(default=False, verbose_name='пометка удаленности')
    additional_info = JSONField("Дополнительные настройки", blank=True, default=dict)

    class Meta:
        """
        Настройки модели.

        Модель является абстрактной.
        """

        abstract = True


class WhoIdMixin(models.Model):
    """
    Примесь идентификации пользователя, который выполнил действия над объектом.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Создана пользователем',
        on_delete=models.PROTECT,
        related_name="created_%(class)s",
        null=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Последний изменивший пользователь',
        on_delete=models.PROTECT,
        related_name="updated_%(class)s_related",
        null=True
    )

    class Meta:
        """
        Настройки  примеси.
        """
        abstract = True
