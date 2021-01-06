from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

COMMON_READ_ONLY_FIELDS = [
    'id', 'created_by', 'modified_by', 'created_at', 'updated_at'
]


class CommonAdmin(admin.ModelAdmin):
    readonly_fields = COMMON_READ_ONLY_FIELDS

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
