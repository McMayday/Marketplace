from django.urls import re_path
from rest_framework import routers
from mediastore.api import FileUploadView


router = routers.DefaultRouter()
router.register('', FileUploadView, basename='media_upload')


# urlpatterns = [
#     # ...
#     re_path(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view())
# ]