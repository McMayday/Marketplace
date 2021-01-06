from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from users.models import GeneralAccount

COMMON_READ_ONLY_FIELDS = [
    'id', 'created_by', 'modified_by', 'date_joined', 'updated_at', 'last_login'
]


@admin.register(GeneralAccount)
class CommonDirectoryAdmin(UserAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    list_display = ('id', 'username', 'email', 'account_type', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'middle_name', 'email')}),
        (_('Personal info'), {
            'fields': ('organization_title', 'avatar', 'account_type', 'skills', 'contacts_info', 'additional_info')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'updated_at', 'created_by', 'modified_by')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    readonly_fields = COMMON_READ_ONLY_FIELDS
