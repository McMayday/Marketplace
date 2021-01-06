from django.contrib.auth import get_user_model
from rest_framework import serializers

COMMON_FIELDS = (
    'id',
    'first_name',
    'last_name',
    'middle_name',
    'organization_title',
    'organization_description',
    'avatar',
    'date_joined',
    'account_type',
    'date_joined',
    'updated_at'
)


class RecruiterPublicInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор организации.
    Публичной части
    """

    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        fields = COMMON_FIELDS
        read_only_fields = COMMON_FIELDS


class RecruiterInfoSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        fields = COMMON_FIELDS + ('contacts_info', )
        read_only_fields = COMMON_FIELDS + ('contacts_info', )
