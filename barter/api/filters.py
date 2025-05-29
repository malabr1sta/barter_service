from django_filters import rest_framework as filters
from ads import models as ads_models
from django.db.models import Q


class ExchangeProposalFilter(filters.FilterSet):
    other_user = filters.NumberFilter(method='filter_other_user')
    role = filters.CharFilter(method='filter_role')

    class Meta:
        model = ads_models.ExchangeProposal
        fields = ['status', 'other_user', 'role']

    def filter_other_user(self, queryset, name, value):
        return queryset.filter(
            Q(ad_sender__user__id=value) |
            Q(ad_receiver__user__id=value)
        )

    def filter_role(self, queryset, name, value):
        user = self.request.user
        if value == ads_models.ExchangeProposal.SENDER:
            return queryset.filter(ad_sender__user=user)
        elif value == ads_models.ExchangeProposal.RECEIVER:
            return queryset.filter(ad_receiver__user=user)
        return queryset
