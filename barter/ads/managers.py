from django.db import models


class ActiveManager(models.Manager):
    """Менеджер для исключения всех удаленных объектов"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=True)
