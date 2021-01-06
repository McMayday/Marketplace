import django_filters
from django.contrib.auth import get_user_model

from shared.filtersets import JSONKeysFilterSet


class UserInfoFilterSet(JSONKeysFilterSet):
    """
    Описание параметров.
    """

    skills_all = django_filters.CharFilter(
        field_name='skills', method='filter_contains_all', help_text="skill1,skill2,skill3", label="testlabel"
    )
    skills_any = django_filters.CharFilter(
        field_name='skills', method='filter_contains_any', help_text="skill1,skill2,skill3"
    )

    class Meta:
        model = get_user_model()
        fields = ['date_joined']