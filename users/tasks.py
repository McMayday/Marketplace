from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_message(subject, context, email):
    """
    Задача для отправки уведомления по электронной почте при успешном создании аккаунта.
    """
    
    message = 'Для того чтобы подтвердить регистрацию на платформе Opemind, пройдите по ссылке\n\n\
                {}.'.format(context)
    mail_sent = send_mail(subject,
                          message,
                          settings.EMAIL_HOST_USER,
                          [email])
    return mail_sent
