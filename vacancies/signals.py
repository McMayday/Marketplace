from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from vacancies.models import Vacancy
from vacancies.tasks import moderation_vacancy_status_notification
from vacancies.vacancies_constants import \
    VACANCY_STATUS_APPROVED, \
    VACANCY_STATUS_PUBLISHED, \
    VACANCY_RESPOND_STATUS_REJECTED, \
    VACANCY_STATUS_BLOCKED

EMAIL_ACTION_STATUSES = [
    VACANCY_STATUS_APPROVED,
    VACANCY_STATUS_PUBLISHED,
    VACANCY_RESPOND_STATUS_REJECTED,
    VACANCY_STATUS_BLOCKED
]


@receiver(pre_save, sender=Vacancy)
def catch_previous_vacancy_status(sender, instance: Vacancy, **kwargs):
    try:
        old_data: Vacancy = Vacancy.objects.get(id=instance.pk)
    except Vacancy.DoesNotExist:
        pass
    else:
        instance.context['is_status_changed'] = old_data.status != instance.status


@receiver(post_save, sender=Vacancy)
def notify_vacancy_status_changed(sender, instance: Vacancy, created, **kwargs):
    if instance.context.get('is_status_changed'):
        if instance.status in EMAIL_ACTION_STATUSES:
            moderation_vacancy_status_notification.delay(str(instance.id), instance.status_human)
