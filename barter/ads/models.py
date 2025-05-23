from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.db import models

from ads import (
    constants as ads_constants,
    managers as base_managers
)


User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='создан'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name='обновлен'
    )
    deleted = models.BooleanField(default=False, verbose_name='Удален?')

    objects = models.Manager()
    active_objects = base_managers.ActiveManager()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at', 'updated_at']
        abstract = True


class Ad(BaseModel):

    BOOKS = 'books'
    CLOTHES = 'clothes'
    SHOES = 'shoes'
    ELECTRONICS = 'electronics'
    TOYS = 'toys'
    FURNITURE = 'furniture'
    SPORTS = 'sports'
    KITCHEN = 'kitchen'
    ACCESSORIES = 'accessories'
    TOOLS = 'tools'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (BOOKS, 'Книги'),
        (CLOTHES, 'Одежда'),
        (SHOES, 'Обувь'),
        (ELECTRONICS, 'Электроника'),
        (TOYS, 'Игрушки'),
        (FURNITURE, 'Мебель'),
        (SPORTS, 'Спорттовары'),
        (KITCHEN, 'Кухонная утварь'),
        (ACCESSORIES, 'Аксессуары'),
        (TOOLS, 'Инструменты'),
        (OTHER, 'Другое'),
    ]

    NEW = 'new'
    USED = 'used'

    CONDITION_CHOICES = [
        (NEW, 'Новый'),
        (USED, 'Б/У'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь'
    )
    title = models.CharField(max_length=50, verbose_name='название')
    description = models.TextField(
        verbose_name='описание',
        validators=[MaxLengthValidator(500)]
    )
    image_url = models.ImageField(
        null=True,
        blank=True,
        upload_to=ads_constants.PATH_UPLOAD_IMAGE,
        verbose_name='ссылка на изображение'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='категория'
    )
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        verbose_name='состояние'
    )

    def __str__(self):
        return self.title

    def has_accepted_proposal(self):
        """
        Проверяет, есть ли у данного объявления
        хотя бы одно принятое предложение обмена.

        Возвращает:
            bool: True, если есть принятое предложение, иначе False.
        """
        return (
            self.sent_proposals.filter(status='accepted').exists() or
            self.received_proposals.filter(status='accepted').exists()
        )

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class DeletedAd(Ad):

    class Meta:
        proxy = True
        verbose_name = "Объявление удаленное"
        verbose_name_plural = "Объявления удаленные"


class ExchangeProposal(BaseModel):

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'

    STATUS_CHOICES = [
        (PENDING, 'Ожидает'),
        (ACCEPTED, 'Принят'),
        (DECLINED, 'Отклонен'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        related_name='sent_proposals',
        on_delete=models.CASCADE,
        verbose_name='предложение отправителя'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        related_name='received_proposals',
        on_delete=models.CASCADE,
        verbose_name='предложение получателя'
    )
    comment = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(500)],
        verbose_name='комментарий'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='статус'
    )

    def __str__(self):
        return f"{self.ad_sender}/{self.ad_receiver}"

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
