import django_filters
from django.contrib.auth import get_user_model

from users import users_constants


class RecruitersFilters(django_filters.FilterSet):
    """
    Описание параметров.
    """

    account_type = django_filters.ChoiceFilter(
        field_name='account_type',
        help_text="\_\_HIRER\_\_,\_\_ORGANIZATION\_\_",
        choices=users_constants.HIRER_TYPES
    )

    class Meta:
        model = get_user_model()
        fields = {
            'account_type': ['exact']
        }
