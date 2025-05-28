from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
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

    @classmethod
    def get_available_ads_for_exchange(cls, ad_receiver, user):
        """
        Возвращает QuerySet объявлений пользователя `user`,
        которые можно предложить в обмен на `ad_receiver`.

        Аргументы:
            user (User): Пользователь, чьи объявления ищутся.
            ad_receiver (Ad): Объявление, на которое хотят обменять.

        Возвращает:
            QuerySet: Доступные для обмена объявления пользователя.
        """

        # Исключаем объявления с "pending" предложением к ad_receiver
        exclude_received = Q(
            received_proposals__status='pending',
            received_proposals__ad_sender=ad_receiver
        )

        # Исключаем объявления с "pending" предложением от ad_receiver
        exclude_sent = Q(
            sent_proposals__status='pending',
            sent_proposals__ad_receiver=ad_receiver
        )
        return (
            cls.active_objects
            .filter(user=user)
            .exclude(user=getattr(ad_receiver, "user", None))
            .exclude(exclude_received)
            .exclude(exclude_sent)
        )

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

    def save(self, *args, **kwargs):
        if self.pk is not None and self.deleted:
            old = get_object_or_404(Ad, pk=self.pk)
            if old.deleted != self.deleted:
                self.received_proposals.filter(
                    deleted=False,
                    status=ExchangeProposal.PENDING
                ).update(status=ExchangeProposal.DECLINED)
                self.sent_proposals.filter(
                    deleted=False,
                    status=ExchangeProposal.PENDING
                ).update(status=ExchangeProposal.DECLINED)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
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

    SENDER = 'sender'
    RECEIVER = 'receiver'

    ROLE_CHOICES = [
        (SENDER, 'Отправитель'),
        (RECEIVER, 'Получатель'),
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
    comment_sender = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(500)],
        verbose_name='комментарий отправителя'
    )
    comment_receiver = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(500)],
        verbose_name='комментарий получателя'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='статус'
    )

    @classmethod
    def cancel_related_proposals(cls, ad_sender, ad_receiver):
        """
        Отменяет все предложения, где ad_sender или ad_receiver участвуют
        как отправитель или получатель.
        """
        cls.objects.filter(
            (Q(ad_sender=ad_sender) |
             Q(ad_receiver=ad_sender) |
             Q(ad_sender=ad_receiver) |
             Q(ad_receiver=ad_receiver)),
            status=ExchangeProposal.PENDING
        ).update(status=ExchangeProposal.DECLINED)

    @classmethod
    def get_user_proposals(cls, user):
        """
        Возвращает QuerySet всех предложений обмена,
        в которых пользователь участвует
        как отправитель или получатель.
        """
        return cls.objects.filter(
            Q(ad_sender__user=user) | Q(ad_receiver__user=user)
        ).select_related('ad_sender', 'ad_receiver')

    def _mark_ads_deleted(self):
        """
        Помечает оба объявления (отправителя и получателя) как deleted=True.
        """
        self.ad_sender.deleted = True
        self.ad_sender.save(update_fields=['deleted'])
        self.ad_receiver.deleted = True
        self.ad_receiver.save(update_fields=['deleted'])

    def _has_just_been_accepted(self):
        """
        Возвращает True, если:
        - объект новый (ещё не был сохранён) и его статус — ACCEPTED
        - объект уже существовал, статус был НЕ ACCEPTED, теперь стал ACCEPTED
        """
        if self.status != self.ACCEPTED:
            return False
        if self.pk is None:
            return True  # Новый объект сразу создаётся с ACCEPTED
        old = get_object_or_404(ExchangeProposal, pk=self.pk)
        return old.status != self.ACCEPTED

    def save(self, *args, **kwargs):
        if self._has_just_been_accepted():
            self._mark_ads_deleted()
            self.cancel_related_proposals(self.ad_sender, self.ad_receiver)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ad_sender}/{self.ad_receiver}"

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
