from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import JSONField
from transitions import Machine

from shared.models import BaseModel, WhoIdMixin
from vacancies.vacancies_constants import VACANCY_STATUSES, VACANCY_STATUS_NEW, VACANCY_RESPOND_STATUSES, \
    VACANCY_RESPOND_STATUS_NEW, VACANCY_STATUSES_DICT, VACANCY_RESPOND_STATUSES_LIST, \
    VACANCY_RESPOND_STATUS_REJECTED, VACANCY_RESPOND_STATUS_WITHDRAWN, \
    VACANCY_RESPOND_STATUS_APPROVED, VACANCY_RESPOND_STATUS_DONE, VACANCY_RESPOND_STATUS_FAIL, \
    VACANCY_RESPOND_STATUS_CANCELLED


class Vacancy(WhoIdMixin, BaseModel):
    """
    Модель вакансии
    """

    def __init__(self, *args, **kwargs):
        """
        Добавление свойства. контекста обекта.
        """
        super().__init__(*args, **kwargs)
        self.context = {}

    recruiter = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name='recruiter', related_query_name='recruiter'
    )
    status = models.CharField('Статус', choices=VACANCY_STATUSES, default=VACANCY_STATUS_NEW, max_length=100)
    title = models.CharField('Название вакансии', max_length=1000)
    description = models.TextField('Описание вакансии', max_length=10000)
    salary = models.CharField('Зарплата', max_length=100)
    location = models.CharField('Локация', max_length=1000)
    description_file = models.CharField('Логотип', max_length=1000, blank=True, null=True)

    skills = JSONField("Требуемы навыки", blank=True, default=dict)
    reject_reasons = JSONField("Причины блокировки", blank=True, default=dict)

    responders = models.ManyToManyField(
        get_user_model(),
        through='VacancyRespond',
        through_fields=('vacancy', 'account'),
        related_name='responders', related_query_name='responders'
    )

    @property
    def status_human(self):
        """
        Человекочитаемы статус.
        :return:
        """
        return VACANCY_STATUSES_DICT[self.status]


class VacancyRespond(WhoIdMixin, BaseModel):
    """
    Отклик на Вакансию
    """
    MAX_RATING_VALUE = 5

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    account = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = models.TextField('Дополнительная информация', max_length=10000, blank=True, null=True)
    status = models.CharField(
        'Статус', choices=VACANCY_RESPOND_STATUSES, default=VACANCY_RESPOND_STATUS_NEW, max_length=100
    )
    recruiter_comment = models.TextField('Коментрий нанимателя', max_length=3000, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        'Оценка проделанной работы',
        validators=[MaxValueValidator(MAX_RATING_VALUE)],
        blank=True, null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_state_machine = Machine(
            model=self,
            states=VACANCY_RESPOND_STATUSES_LIST,
            initial=self.status
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_APPROVED,
            source=VACANCY_RESPOND_STATUS_NEW,
            dest=VACANCY_RESPOND_STATUS_APPROVED,
            after='set_state'
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_DONE,
            source=VACANCY_RESPOND_STATUS_APPROVED,
            dest=VACANCY_RESPOND_STATUS_DONE,
            after='set_state'
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_FAIL,
            source=VACANCY_RESPOND_STATUS_APPROVED,
            dest=VACANCY_RESPOND_STATUS_FAIL,
            after='set_state'
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_CANCELLED,
            source=VACANCY_RESPOND_STATUS_APPROVED,
            dest=VACANCY_RESPOND_STATUS_CANCELLED,
            after='set_state'
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_REJECTED,
            source=VACANCY_RESPOND_STATUS_NEW,
            dest=VACANCY_RESPOND_STATUS_REJECTED,
            after='set_state'
        )
        self.status_state_machine.add_transition(
            trigger=VACANCY_RESPOND_STATUS_WITHDRAWN,
            source=VACANCY_RESPOND_STATUS_NEW,
            dest=VACANCY_RESPOND_STATUS_WITHDRAWN,
            after='set_state'
        )

    def set_state(self):
        self.status = self.state

    class Meta:
        """
        Настройки модели.
        """
        unique_together = ['vacancy', 'account']
