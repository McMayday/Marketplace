import django_filters

from vacancies.models import Vacancy


class JSONKeysFilterSet(django_filters.FilterSet):
    """
    Описание параметров.
    """

    skills_all = django_filters.CharFilter(
        field_name='skills', method='filter_contains_all', help_text="skill1,skill2,skill3", label="testlabel"
    )
    skills_any = django_filters.CharFilter(
        field_name='skills', method='filter_contains_any', help_text="skill1,skill2,skill3"
    )

    @staticmethod
    def _transform_query_to_lookup(lookup, queryset, name: str, value: str):
        """
        Преобразование из строки параметров в список.
        И создание фильтра.
        :return:
        """
        values_array = value.split(',')
        look_up = {
            f'{name}__{lookup}': values_array
        }
        return queryset.filter(**look_up)

    def filter_contains_all(self, queryset, name: str, value: str):
        """
        Фильтр содержания объектов содержащих все требуемые скилы.
        :param queryset:
        :param name:
        :param value:
        :return:
        """
        return self._transform_query_to_lookup('has_keys', queryset, name, value)

    def filter_contains_any(self, queryset, name, value):
        """
        Фильтр содержания объектов содержащих хотябы один скилл.
        :param queryset:
        :param name:
        :param value:
        :return:
        """
        return self._transform_query_to_lookup('has_any_keys', queryset, name, value)
