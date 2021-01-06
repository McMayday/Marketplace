from rest_framework import routers

from skills.api import SkillsListViewSet

router = routers.DefaultRouter()
router.register(r'', SkillsListViewSet)
