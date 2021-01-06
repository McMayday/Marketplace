import datetime
import io
import uuid
from pathlib import Path

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, response, viewsets, mixins, views
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser

from app.settings import BASE_DIR, MEDIA_ROOT

CONTENT_DOMAIN_DOCUMENT = "documents"
CONTENT_DOMAIN_IMAGES = "images"

ALLOWED_DOMAINS_MAPPER = {
    CONTENT_DOMAIN_DOCUMENT: ['application/pdf'],
    CONTENT_DOMAIN_IMAGES: ['image/jpeg', 'image/png']
}


class MediaUploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)


class UploadedFileLinkSrializer(serializers.Serializer):
    file_link = serializers.CharField(required=True, label='Ссылка на файл контента', max_length=1300)


class FileUploadView(viewsets.GenericViewSet):
    """
    Загрузка файла для соответвующей доменной области контента

    Доступны следующие доменные области:
    ***documents*** - предназначенные для сохранения документов
        - Доступные content/type - (application/pdf)
    **images** - предназначенные для сохранения картинок
        - Доступные content/type - (image/jpeg,image/png)

    """
    parser_classes = [FileUploadParser]
    lookup_url_kwarg = 'domain'

    # TODO перенести логику в сериалайзер.
    def check_content_type(self, domain, request):
        """
        Проверка на домен и тип контента.
        :return:
        """
        try:
            allowed_content_types = ALLOWED_DOMAINS_MAPPER[domain]
        except KeyError:
            raise serializers.ValidationError("Bad domain name")
        file = request.FILES['file']
        if file.content_type not in allowed_content_types:
            raise serializers.ValidationError(f"Bad content-type for domain {domain}")
        return file, file.name

    @swagger_auto_schema(
        request_body=MediaUploadFileSerializer(),
        responses={201: UploadedFileLinkSrializer()},
    )
    @action(detail=True, methods=['put'], parser_classes=(MultiPartParser, FileUploadParser))
    def upload(self, request, domain):
        MediaUploadFileSerializer(data=request.data).is_valid(raise_exception=True)
        file, name = self.check_content_type(domain, request)
        now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = Path(name).suffix
        path_to_media = Path(BASE_DIR, MEDIA_ROOT, domain, datetime.date.today().isoformat())
        path_to_media.mkdir(exist_ok=True, parents=True)
        ident = uuid.uuid4()
        file_name = f"{now_time}_{request.user.id}_{ident}{file_ext}"
        file_name = Path(path_to_media, file_name)
        file_name.write_bytes(file.read())
        file_media_link = str(file_name).replace(str(BASE_DIR), '')
        return response.Response({
            'file_link': file_media_link
        }, status=status.HTTP_201_CREATED)
