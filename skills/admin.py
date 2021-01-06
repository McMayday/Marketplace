from django.contrib import admin

from shared.admin import CommonAdmin
from skills.models import Skill


@admin.register(Skill)
class VacancyAdmin(CommonAdmin):
    list_display = [
        'id', 'title', 'created_by', 'modified_by', 'updated_at', 'created_at'
    ]
