from rest_framework import filters, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from api import serializers as api_serializers
from ads import (
    models as ads_models,
    utils as ads_utils
)


class AdViewSet(viewsets.ModelViewSet):
    queryset = ads_models.Ad.active_objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = api_serializers.AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['category', 'condition', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']

    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """Возвращает список всех категорий"""
        return Response([c[0] for c in ads_models.Ad.CATEGORY_CHOICES])

    @action(detail=False, methods=['get'], url_path='conditions')
    def conditions(self, request):
        """Возвращает список всех состояний"""
        return Response([c[0] for c in ads_models.Ad.CONDITION_CHOICES])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        ad = self.get_object()
        try:
            ads_utils.can_edit_ad(ad, self.request.user)
        except PermissionDenied:
            raise DRFPermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise DRFPermissionDenied()
        instance.deleted = True
        instance.save()


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ads_models.ExchangeProposal.objects.all()
    serializer_class = api_serializers.ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'ad_sender', 'ad_receiver']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        return ads_models.ExchangeProposal.get_user_proposals(user)

    def perform_create(self, serializer):
        serializer.save()
