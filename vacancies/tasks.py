from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from app.settings import EMAIL_SUBJECT_PREFIX, EMAIL_HOST_USER, CURRENT_DOMAIN, VACANCIES_FRONTEND_URI
from vacancies.models import Vacancy

CHANGE_VACANCY_STATUS_EMAIL_SUBJECT = f'[{EMAIL_SUBJECT_PREFIX}] Изменение статуса вакансии'
VACANCY_EMAIL_TEMPLATE = 'vacancies/change_status_email.html'


@shared_task
def moderation_vacancy_status_notification(vacancy_id: str, new_status: str):
    """
    Отправка писем об изменении статуса вакансии.
    :return:
    """
    vacancy: Vacancy = Vacancy.existing_objects.get(id=vacancy_id)
    email_body = render_to_string(
        VACANCY_EMAIL_TEMPLATE,
        context={
            "target_host": CURRENT_DOMAIN,
            "vacancies_uri": VACANCIES_FRONTEND_URI,
            "email_title": CHANGE_VACANCY_STATUS_EMAIL_SUBJECT,
            "vacancy_id": vacancy_id,
            "vacancy_title": vacancy.title,
            "vacancy_status": new_status
        }
    )
    members = vacancy.organization.members.filter(is_active=True)
    emails = []
    for user in members:
        target_email = user.email
        if type(user.contacts_info) is dict:
            target_email = user.contacts_info.get('email', user.email)
        if target_email:
            emails.append(target_email)

    results = send_mail(
        CHANGE_VACANCY_STATUS_EMAIL_SUBJECT,
        email_body,
        EMAIL_HOST_USER,
        emails,
        html_message=email_body
    )
    return results
