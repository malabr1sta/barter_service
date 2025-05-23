from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models.query import QuerySet
from typing import Union


def paginator_method(
    request: HttpRequest,
    objects: Union[QuerySet, list],
    number_per_page: int
):
    """
    Возвращает объект страницы для пагинации.
    """
    paginator = Paginator(objects, number_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def can_edit_ad(ad, user) -> bool:
    """
    Проверяет, может ли пользователь редактировать объявление.

    Возвращает False, если:
    - пользователь не автор объявления
    - объявление помечено как удалённое
    - у объявления уже есть принятая заявка на обмен
    """
    return ad.user == user and not ad.deleted and not ad.has_accepted_proposal()

