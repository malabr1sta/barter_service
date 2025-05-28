from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q

from ads import (
    constants as ads_constants,
    forms as ads_forms,
    models as ads_models,
    utils as ads_utils
)


def index_page(request):
    """
    Главная страница:
    Доступные GET-параметры:
      - q: поисковый запрос по заголовку и описанию
      - category: фильтрация по категории
      - condition: фильтрация по состоянию товара
      - user: фильтрация по пользователю (id)
    """
    get_params = request.GET.copy()
    category = get_params.get('category', '')
    condition = get_params.get('condition', '')
    user = get_params.get('user', '')
    query = get_params.get('q', '')
    get_params.pop('page', None)

    filters = {
        'category': category,
        'condition': condition,
        'user__id': user,
    }

    # Удаляем пустые значения
    filters = {key: value for key, value in filters.items() if value}

    #Получит все Ads у которых нет принятых предложений
    ads = ads_models.Ad.active_objects.all()
    if query:
        ads = ads.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    ads = ads.filter(**filters)

    page_obj = ads_utils.paginator_method(
        request, ads, ads_constants.ADS_PER_PAGE
    )
    context = {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'condition': condition,
        'user': user,
        'category_choices': ads_models.Ad.CATEGORY_CHOICES,
        'condition_choices': ads_models.Ad.CONDITION_CHOICES,
        'extra_query': get_params.urlencode(),
    }

    return render(request, ads_constants.TEMPATE_INDEX_PAGE, context)


@login_required
def ad_create(request):
    """
    Создание нового объявления.
    """
    form = ads_forms.AdForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        ad = form.save(commit=False)
        ad.user = request.user
        ad.save()
        return redirect('ads:index_page')
    return render(
        request,
        ads_constants.TEMPATE_AD_CREATE_PAGE,
        {'form': form}
    )


@login_required
def ad_update(request, pk):
    """
    Обновление объявления.
    """

    ad = get_object_or_404(ads_models.Ad, pk=pk)

    ads_utils.can_edit_ad(ad, request.user)

    form = ads_forms.AdForm(
        request.POST or None,
        request.FILES or None,
        instance=ad
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('ads:index_page')

    context = {
        'form': form,
        'ad': ad,
    }

    return render(request, ads_constants.TEMPATE_AD_UPDATE_PAGE, context)


@login_required
def ad_soft_delete(request, pk):
    """
    Удалениe объявления.
    """

    ad = get_object_or_404(ads_models.Ad, pk=pk)

    ads_utils.can_edit_ad(ad, request.user)

    if request.method == 'POST':
        ad.deleted = True
        ad.save()
        return redirect('ads:index_page')


@login_required
def proposal_create(request, ad_receiver_pk):
    """
    Создание предложения обмена.
    """
    ad_receiver = get_object_or_404(ads_models.Ad, pk=ad_receiver_pk)
    form = ads_forms.ExchangeProposalForm(
        request.POST or None,
        ad_receiver=ad_receiver,
        user=request.user
    )

    if request.method == 'POST' and form.is_valid():
        proposal = form.save(commit=False)
        proposal.ad_receiver = ad_receiver
        proposal.save()
        return redirect('ads:index_page')

    context = {'form': form, 'ad_receiver': ad_receiver}

    return render(
        request,
        ads_constants.TEMPATE_PROPOSAL_CREATE_PAGE,
        context
    )


@login_required
def proposals_list(request):
    """
    Отображает список предложений обмена для текущего пользователя.
    Доступные GET-параметры:
        - status: по статусу предложения (ожидает, принят, отклонен)
        - other_user: по другому пользователю, с которым есть предложения
        - role: по роли пользователя в предложении (отправитель или получатель)
    """
    get_params = request.GET.copy()
    status = get_params.get('status', '')
    other_user_id = get_params.get('other_user', '')
    role = get_params.get('role', '')
    get_params.pop('page', None)

    user = request.user

    proposals = ads_models.ExchangeProposal.get_user_proposals(user)

    if status:
        proposals = proposals.filter(status=status)

    # Фильтрация по другому пользователю
    if other_user_id:
        proposals = proposals.filter(
            Q(ad_sender__user__id=other_user_id) |
            Q(ad_receiver__user__id=other_user_id)
        )

    # Фильтрация по роли пользователя в предложении
    if role == ads_models.ExchangeProposal.SENDER:
        proposals = proposals.filter(ad_sender__user=user)
    elif role == ads_models.ExchangeProposal.RECEIVER:
        proposals = proposals.filter(ad_receiver__user=user)

    page_obj = ads_utils.paginator_method(
        request, proposals,
        ads_constants.PROPOSAL_PER_PAGE
    )

    context = {
        'page_obj': page_obj,
        'status_choices': ads_models.ExchangeProposal.STATUS_CHOICES,
        'role_choices': ads_models.ExchangeProposal.ROLE_CHOICES,
        'status': status,
        'other_user': other_user_id,
        'role': role,
        'extra_query': get_params.urlencode(),
    }
    return render(request, ads_constants.TEMPATE_PROPOSAL_LIST_PAGE, context)


@login_required
def proposal_update(request, pk):
    """
    редактирование комментарий и статус предложения.
    - Отправитель: только comment_sender и статус "отклонен"
    - Получатель: только comment_receiver и статус "отклонен" или "принят"
    """
    proposal = get_object_or_404(ads_models.ExchangeProposal, pk=pk)
    user = request.user
    form = ads_forms.ExchangeProposalUpdateForm(
        request.POST or None, instance=proposal, user=user
    )

    ads_utils.can_edit_proposal(proposal, user)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('ads:proposals_list')

    return render(request, ads_constants.TEMPATE_PROPOSAL_UPDATE_PAGE, {
        "form": form,
        "proposal": proposal,
    })
