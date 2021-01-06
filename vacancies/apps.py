from django.apps import AppConfig


class VacanciesConfig(AppConfig):
    name = 'vacancies'

    def ready(self):
        """
        Подключение сигналов.
        :return:
        """
        # Подключение сигналов не удалять
        from .signals import catch_previous_vacancy_status, notify_vacancy_status_changed