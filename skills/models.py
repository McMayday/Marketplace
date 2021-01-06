from django.db import models
from shared.models import BaseModel, WhoIdMixin


class Skill(WhoIdMixin, BaseModel):
    """
    Модель навыка
    """

    title = models.CharField('Ключ навыка', max_length=200, unique=True)

    def __str__(self):
        """
        Строковое отображение.
        :return:
        """

        return f'{self.title}({self.id})'
