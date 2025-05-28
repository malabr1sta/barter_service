from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.db.models.query import QuerySet
from typing import Union, Sequence, Any

from ads import models as ads_models


def paginator_method(
    request: HttpRequest,
    objects: Union[QuerySet, Sequence[Any]],
    number_per_page: int
):
    """
    Возвращает объект страницы для пагинации.
    """
    paginator = Paginator(objects, number_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def can_edit_ad(ad: ads_models.Ad, user: User):
    """
    Проверяет, может ли пользователь редактировать объявление.

    Выбрасывает PermissionDenied (403), если:
    - пользователь не является автором объявления;
    - объявление помечено как удалённое;
    - у объявления уже есть принятая заявка на обмен.
    """
    if ad.user != user or ad.deleted or ad.has_accepted_proposal():
        raise PermissionDenied


def can_edit_proposal(proposal: ads_models.ExchangeProposal, user: User):
    """
    Проверяет, может ли пользователь редактировать Предложение.

    Выбрасывает PermissionDenied (403), если:
    - пользователь не является отправителем или получателем;
    - объявление не в статусе Ожидания;
    """
    is_sender = proposal.ad_sender.user_id == user.id
    is_receiver = proposal.ad_receiver.user_id == user.id

    if (
        proposal.status != ads_models.ExchangeProposal.PENDING
        or not (is_sender or is_receiver)
    ):
        raise PermissionDenied

