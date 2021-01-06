from django.contrib import admin

from shared.admin import CommonAdmin
from vacancies.models import Vacancy, VacancyRespond


@admin.register(Vacancy)
class VacancyAdmin(CommonAdmin):
    list_filter = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recruiter').order_by('-updated_at')

    list_display = [
        'id', 'recruiter', 'title', 'status', 'created_by', 'modified_by', 'updated_at', 'created_at'
    ]


@admin.register(VacancyRespond)
class VacancyRespondAdmin(CommonAdmin):
    list_filter = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vacancy__recruiter', 'account').order_by('-updated_at')

    list_display = [
        'id', 'vacancy', 'account', 'status', 'description', 'created_by', 'modified_by', 'updated_at', 'created_at'
    ]
