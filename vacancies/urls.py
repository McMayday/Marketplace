from rest_framework import routers

from vacancies.api import PublicVacanciesListViewSet, \
    NewRespondViewSet, RespondControlViewSet, RespondRecruiterControlViewSet, PersonalVacancyRespondViewSet, \
    VacancyOrganizationControlStatusViewSet, RecruiterVacanciesViewSet

router = routers.DefaultRouter()
router.register(r'self', RecruiterVacanciesViewSet)
router.register(r'self/change-status', VacancyOrganizationControlStatusViewSet)
router.register(r'responds/create', NewRespondViewSet)
router.register(r'responds/personal', RespondControlViewSet)
router.register(r'responds/recruiter', RespondRecruiterControlViewSet)
router.register(r'', PersonalVacancyRespondViewSet)
router.register(r'', PublicVacanciesListViewSet)

