from django.contrib.auth import get_user_model
from rest_framework import serializers

from users import users_constants
from users.serializers import UserInfoSerializer
from vacancies.models import Vacancy, VacancyRespond
from vacancies.vacancies_constants import VACANCY_STATUS_PUBLISHED, VACANCY_STATUS_ARCHIVED, VACANCY_STATUS_UNPUBLISHED, \
    VACANCY_RESPOND_STATUS_APPROVED, VACANCY_RESPOND_STATUS_REJECTED, VACANCY_RESPOND_STATUS_DONE, \
    VACANCY_RESPOND_STATUS_FAIL, VACANCY_RESPOND_STATUS_CANCELLED


class VacancyRecruitersPublicInfo(serializers.ModelSerializer):
    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        fields = ['id', 'organization_title', 'first_name', 'last_name', 'middle_name', 'account_type']
        read_only_fields = [
            'id', 'organization_title', 'first_name', 'last_name', 'middle_name', 'account_type'
        ]


class PublicVacancySerializer(serializers.ModelSerializer):
    published_recruiter = VacancyRecruitersPublicInfo(source='recruiter')

    class Meta:
        """
        Настройки сериализатора.
        """
        model = Vacancy
        exclude = ['created_by', 'modified_by', 'is_deleted', 'reject_reasons', 'status']
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class RecruiterVacanciesSerializer(serializers.ModelSerializer):

    @staticmethod
    def validate_skills(skills):
        """
        Набор навыков должен быть объектом.
        :param skills:
        :return:
        """
        if type(skills) is not dict:
            raise serializers.ValidationError(f'skills must be object with key -> skill any value ')
        else:
            return skills

    def create(self, validated_data):
        """
        При создании вакансии проставляется создавший ее пользователь.
        Вакансии может создавать только пользоваетль стипом аккаунта
        '__HIRER__' или '__ORGANISATION__'
        :param validated_data:
        :return:
        """
        user = self.context['request'].user

        if user.account_type not in [
            users_constants.USER_ACCOUNT_TYPE_ORGANIZATION, users_constants.USER_ACCOUNT_TYPE_HIRER
        ]:
            raise serializers.ValidationError(f'Only recruiter accounts can create vacancy')
        validated_data['recruiter'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        """
        Настройки сериализатора.
        """
        model = Vacancy
        exclude = ['is_deleted', 'recruiter']
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
            'modified_by', 'reject_reasons', 'status'
        ]


class NewRespondSerializer(serializers.ModelSerializer):

    def validate_vacancy(self, vacancy):
        """
        :param vacancy:
        :return:
        """
        if vacancy.status != VACANCY_STATUS_PUBLISHED:
            raise serializers.ValidationError(f'Vacancy must be in {VACANCY_STATUS_PUBLISHED} status')
        return vacancy

    def create(self, validated_data):
        """
        Подстановка создавшего пользователя в отклик.
        Отклик может создать только пользователь с типом аккаунта
        __APPLICANT__
        """
        user = self.context['request'].user

        if user.account_type not in [
            users_constants.USER_ACCOUNT_TYPE_APPLICANT
        ]:
            raise serializers.ValidationError(f'Only applicants can create responds')

        validated_data['account'] = user
        return super().create(validated_data)

    class Meta:
        """
        Настройки сериализатора.
        """
        model = VacancyRespond
        fields = ['vacancy', 'description', 'id', 'created_at', 'updated_at', 'modified_by', 'status']
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
            'modified_by', 'reject_reasons', 'status'
        ]


class VacancyInfo(serializers.ModelSerializer):
    class Meta:
        """
        Настройки сериализатора.
        """
        model = Vacancy
        fields = ['id', 'title', 'status']
        read_only_fields = [
            'id', 'title', 'status'
        ]


class PersonalRespondSerializer(serializers.ModelSerializer):
    target_vacancy_data = VacancyInfo(source='vacancy')

    class Meta:
        """
        Настройки сериализатора.
        """
        model = VacancyRespond
        fields = ['vacancy', 'account', 'description', 'id',
                  'created_at', 'updated_at', 'modified_by', 'status', 'target_vacancy_data',
                  'recruiter_comment', 'rating'
                  ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
            'modified_by', 'reject_reasons', 'status', 'vacancy', 'account', 'recruiter_comment', 'rating'
        ]


class RecruiterRespondSerializer(serializers.ModelSerializer):
    target_vacancy_data = VacancyInfo(source='vacancy')
    target_user_data = UserInfoSerializer(source='account')

    class Meta:
        """
        Настройки сериализатора.
        """
        model = VacancyRespond
        fields = [
            'account', 'description', 'id',
            'created_at', 'updated_at', 'modified_by', 'recruiter_comment', 'rating',
            'status', 'target_vacancy_data', 'target_user_data',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
            'modified_by', 'status', 'account', 'target_user_data', 'target_vacancy_data', 'recruiter_comment', 'rating'
        ]


class RespondStatusChangeSerializerByRecruiter(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            VACANCY_RESPOND_STATUS_APPROVED,
            VACANCY_RESPOND_STATUS_REJECTED,
        ]
    )


class RespondStatusChangeWithCommentSerializerByRecruiter(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            VACANCY_RESPOND_STATUS_DONE,
            VACANCY_RESPOND_STATUS_FAIL,
            VACANCY_RESPOND_STATUS_CANCELLED
        ]
    )
    comment = serializers.CharField(help_text='Коментрий', required=False, max_length=3000)
    rating = serializers.IntegerField(
        help_text='Оценка выполненной работы', required=False, min_value=0, max_value=VacancyRespond.MAX_RATING_VALUE
    )


AVAILABLE_STATUSES_TO_CHANGE = [
    VACANCY_STATUS_PUBLISHED, VACANCY_STATUS_ARCHIVED, VACANCY_STATUS_UNPUBLISHED
]


class RecruiterVacancyStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=AVAILABLE_STATUSES_TO_CHANGE)

    class Meta:
        """
        Настройки сериализатора.
        """
        model = VacancyRespond
        fields = ['id', 'status']
        read_only_fields = ['id']
