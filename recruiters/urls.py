from rest_framework import routers

from recruiters.api import RecruiterDetailedReadOnlyView, RecruiterReadOnlyView


router = routers.DefaultRouter()
router.register(r'detailed', RecruiterDetailedReadOnlyView)
router.register(r'', RecruiterReadOnlyView)
