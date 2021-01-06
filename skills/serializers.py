from rest_framework import serializers

from skills.models import Skill


class PublicSkillListSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Настройки сериализатора.
        """
        model = Skill
        fields = ['id', 'title', 'additional_info']
        read_only_fields = ['id', 'title', 'additional_info']
