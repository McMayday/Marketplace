"""openmind URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from app import settings
from app.swagger_config import swagger_url_patterns

# Pоутеры
from users.urls import router as users_router
from recruiters.urls import router as organizations_router
from vacancies.urls import router as vacancy_router
from mediastore.urls import router as media_router
from skills.urls import router as skills_router

urlpatterns = swagger_url_patterns + [
    path('admin/', admin.site.urls),
    path('api/mediastore/', include(
        (media_router.urls, 'media_api'), namespace='media_api')
         ),
    path('api/users/', include(
        (users_router.urls, 'users_api'), namespace='users_api')
         ),
    path('api/recruiters/', include(
        (organizations_router.urls, 'recruiters_api'), namespace='recruiters_api')
         ),
    path('api/vacancies/', include(
        (vacancy_router.urls, 'vacancy_api'), namespace='vacancy_api')
         ),
    path('api/skills/', include(
        (skills_router.urls, 'skills_api'), namespace='skills_api')
         ),
    path('api/auth/', include(('users.urls', 'users'), namespace='users'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
