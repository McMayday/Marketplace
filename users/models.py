from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import JSONField, Q

from shared.models import WhoIdMixin
from users import users_constants


class AvailableObjectsManager(UserManager):
    """
    Менеджер для работы только "не активные пользователи".
    """

    def get_queryset(self):
        return super().get_queryset().exclude(is_active=False)


class AvailableRecruiterManager(AvailableObjectsManager):
    """
    Менеджер для работы только c активными нанимателями
    организация и частными лицами.
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(account_type=users_constants.USER_ACCOUNT_TYPE_HIRER)
            | Q(account_type=users_constants.USER_ACCOUNT_TYPE_ORGANIZATION)
        )


class AvailableApplicantsManager(AvailableObjectsManager):
    """
    Менеджер для работы только c активными пользователями соискателями
    организация и частными лицами.
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            account_type=users_constants.USER_ACCOUNT_TYPE_APPLICANT
        )


class GeneralAccount(WhoIdMixin, AbstractUser):
    objects = UserManager()
    active_accounts = AvailableObjectsManager()
    active_recruiters_accounts = AvailableRecruiterManager()
    active_applicants_accounts = AvailableApplicantsManager()

    email = models.EmailField('E-mail address', unique=True)

    middle_name = models.CharField('Отчество', max_length=150, blank=True, null=True)

    contacts_info = JSONField("Контактная информация", blank=True, default=dict)

    avatar = models.CharField('Ссылка на аватара, главное фото', max_length=555, blank=True, null=True)

    additional_info = JSONField("Дополнительные настройки", blank=True, default=dict)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')

    skills = JSONField("Навыки пользователя", blank=True, default=dict)

    account_type = models.CharField(
        'Тип аккаунта',
        max_length=50,
        choices=users_constants.USERS_TYPES,
        default=users_constants.USER_ACCOUNT_TYPE_APPLICANT,
        help_text='Обозначает тип аккаунта'
    )

    organization_title = models.CharField('Название организации', max_length=150, blank=True, null=True)
    organization_description = models.TextField('Описание организации', max_length=3000, blank=True, null=True)
    profile_file = models.CharField('Файл профиля комапнии', max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = 'account'
        verbose_name_plural = 'accounts'


    def is_confirmed(self):
        return self.auth_token_set.all().count()
