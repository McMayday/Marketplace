from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, response, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from transitions import MachineError

from vacancies.filtersets import VacancyFilters
from vacancies.models import Vacancy, VacancyRespond
from vacancies.serializers import PublicVacancySerializer, \
    NewRespondSerializer, \
    RecruiterRespondSerializer, PersonalRespondSerializer, RecruiterVacancyStatusSerializer, \
    RespondStatusChangeSerializerByRecruiter, RecruiterVacanciesSerializer, \
    RespondStatusChangeWithCommentSerializerByRecruiter
from vacancies.vacancies_constants import VACANCY_STATUS_PUBLISHED, VACANCY_STATUS_MODIFIED, VACANCY_STATUS_NEW, \
    VACANCY_STATUS_ARCHIVED, VACANCY_STATUS_UNPUBLISHED


class PublicVacanciesListViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Просмотр списка вакансий на сайте.
    """
    permission_classes = (permissions.AllowAny,)
    filterset_class = VacancyFilters

    serializer_class = PublicVacancySerializer

    queryset = Vacancy.existing_objects.select_related('recruiter') \
        .filter(status=VACANCY_STATUS_PUBLISHED) \
        .order_by('-updated_at')


class RecruiterVacanciesViewSet(ModelViewSet):
    """
    Управление вакансией
    При создании вакансии проставляется создавший ее пользователь.
    Вакансии может создавать только пользователь с типом аккаунта
    '__HIRER__' или '__ORGANISATION__'
    """
    serializer_class = RecruiterVacanciesSerializer
    queryset = Vacancy.existing_objects.select_related('recruiter').order_by('-updated_at')

    def get_queryset(self):
        """
        Доступны только вакансии нанимателя.
        :return:
        """
        queryset = super().get_queryset()
        return queryset.filter(recruiter=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.status != VACANCY_STATUS_NEW:
            serializer.instance.status = VACANCY_STATUS_MODIFIED
        serializer.save()

    def perform_destroy(self, instance):
        instance.status = VACANCY_STATUS_ARCHIVED
        instance.save()


class NewRespondViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    Создание отклика на вакансию от лица кандидата.
    Отклик может создать только пользователь с типом аккаунта
    __APPLICANT__
    """
    serializer_class = NewRespondSerializer
    queryset = VacancyRespond.existing_objects.all()


class RespondControlViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    Изменение параметров отклика от лица подавшего их пользователя.
    """
    serializer_class = PersonalRespondSerializer
    queryset = VacancyRespond.existing_objects.all()

    filterset_fields = ['status']

    def get_queryset(self):
        user_id = None if self.request.user.is_anonymous else self.request.user.id
        return super().get_queryset().filter(account_id=user_id)


class PersonalVacancyRespondViewSet(
    # mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Получение откликов по конкретной вакансии для подавшего пользователя.
    На данный момент у вакансии от имени пользователя может быть только один отклик,
    Поэтому список всегда состоит максимум из одного.
    Требуется для понимания на фронтенде может ли кандидат еще раз откликнуться на вакансию.
    TODO перенести функионал в детали вакансии для кандидата.
    """
    serializer_class = PersonalRespondSerializer
    queryset = VacancyRespond.existing_objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().filter(account=self.request.user)

    @swagger_auto_schema(
        responses={200: PersonalRespondSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def responds(self, request, id):
        instances = self.get_queryset().filter(
            vacancy_id=id
        )
        serializer = self.get_serializer(instances, many=True)
        return response.Response(serializer.data)


class RespondRecruiterControlViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    Просмотр и изменение параметров отклика от лица нанимателя, на вакансию которого откликнулись.
    """
    serializer_class = RecruiterRespondSerializer
    queryset = VacancyRespond.existing_objects.select_related('vacancy', 'account').all()

    filterset_fields = ['status']

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = None if self.request.user.is_anonymous else self.request.user.id
        return queryset.filter(vacancy__recruiter_id=user_id)

    def _check_status_transition(
            self,
            input_serializer
    ):
        input_serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        next_status = input_serializer.data.get('status')
        try:
            getattr(instance, next_status)()
        except MachineError as err:
            raise ValidationError(err.args[0])
        return instance

    @swagger_auto_schema(
        method='patch',
        request_body=RespondStatusChangeSerializerByRecruiter(),
        responses={200: RecruiterRespondSerializer()}
    )
    @action(detail=True, methods=['patch'], url_path='process-new')
    def process_new(self, request, **kwargs):
        """
        Изменение статуса отклика со стороны нанимателя.
        Управление новым откликом. Работодатель может принять его или отклонить.
        ```
        __NEW__ -> __APPROVED__,
        __NEW__ ->  __REJECTED__
        ```
        """
        instance = self._check_status_transition(
            RespondStatusChangeSerializerByRecruiter(data=request.data)
        )
        instance.save()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @swagger_auto_schema(
        method='patch',
        request_body=RespondStatusChangeWithCommentSerializerByRecruiter(),
        responses={200: RecruiterRespondSerializer()}
    )
    @action(detail=True, methods=['patch'], url_path='process-in-work')
    def process_in_work(self, request, **kwargs):
        """
        Изменение статуса отклика со стороны нанимателя.
        Управление откликом который был взят в работу.
        ```
        __APPROVED__ -> __CANCELLED__,
        __APPROVED__ -> __DONE__,
        __APPROVED__ ->  __FAIL__
        ```
        """
        input_serializer = RespondStatusChangeWithCommentSerializerByRecruiter(data=request.data)
        instance = self._check_status_transition(
            input_serializer
        )
        instance.recruiter_comment = input_serializer.data.get('comment')
        instance.rating = input_serializer.data.get('rating')
        instance.save()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)


class VacancyOrganizationControlStatusViewSet(
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    Управление статусом.
     - Возможен перевод из статуса PUBLISHED в статус ARCHIVED и в статус в UNPUBLISHED и обратно.
     - Обратно в статус PUBLISHED без прохождения модерации можно перевести только из режима UNPUBLISHED
     - В остальных случаях вакансия будет переведена в статус MODIFIED и будет опубликована только после модерации
     - В статус UNPUBLISHED можно перевести только из режима PUBLISHED при попытке перевести из другого статуса будет ошибка.
    При возникновении данной ошибки нужно выводить сообщение пользователю и актуализировать данные по статусу вакансии на фронте
    - в ARCHIVED из любого статуса.
    """
    serializer_class = RecruiterVacancyStatusSerializer
    queryset = Vacancy.existing_objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        next_status = serializer.validated_data['status']
        if next_status == VACANCY_STATUS_PUBLISHED:
            # обратно в статус PUBLISHED без прохождения модерации можно перевести только из режима UNPUBLISHED
            is_updated = Vacancy.existing_objects \
                .filter(id=serializer.instance.id) \
                .filter(status__in=[VACANCY_STATUS_UNPUBLISHED, VACANCY_STATUS_PUBLISHED]) \
                .update(status=VACANCY_STATUS_PUBLISHED)
            if is_updated:
                instance.status = VACANCY_STATUS_PUBLISHED
                serializer = self.get_serializer(instance)
                return response.Response(serializer.data)
            serializer.validated_data['status'] = VACANCY_STATUS_MODIFIED
        if next_status == VACANCY_STATUS_UNPUBLISHED:
            # обратно в статус UNPUBLISHED можно перевести только из режима PUBLISHED
            is_updated = Vacancy.existing_objects \
                .filter(id=serializer.instance.id) \
                .filter(status=VACANCY_STATUS_PUBLISHED) \
                .update(status=VACANCY_STATUS_UNPUBLISHED)
            if not is_updated:
                raise ValidationError('Forbidden transition to UNPUBLISHED, previous status must be PUBLISHED')
            instance.status = VACANCY_STATUS_UNPUBLISHED
            serializer = self.get_serializer(instance)
            return response.Response(serializer.data)
        serializer.save()
        return response.Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = None if self.request.user.is_anonymous else self.request.user.id
        return queryset.filter(recruiter_id=user_id)
