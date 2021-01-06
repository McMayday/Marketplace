from rest_framework import mixins, viewsets, permissions

from skills.models import Skill
from skills.serializers import PublicSkillListSerializer


class SkillsListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Просмотр списка вакансий на сайте.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = PublicSkillListSerializer
    queryset = Skill.existing_objects.all()
